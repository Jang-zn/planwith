#!/usr/bin/env python3
"""Validate structured conclusions and render a portable, escaped HTML report."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import html
import json
import re
from pathlib import Path
import sys

CRITERIA = ['목표 적합성', '근거', '실행 가능성', '비용·위험', '반박 대응']
RUBRICS = {'discovery': [25, 35, 15, 15, 10], 'business': [20, 25, 20, 25, 10],
           'design': [30, 20, 20, 15, 15], 'engineering': [15, 20, 30, 25, 10],
           'general': [20, 20, 20, 20, 20]}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def text_fields(item, keys, where):
    for key in keys:
        need(isinstance(item.get(key), str) and item[key].strip(), f'{where}: missing {key}')


def load(round_dir):
    root = Path(round_dir).resolve()
    records = root / 'records'
    data = read(records / 'report.json')
    text_fields(data, ['title', 'summary'], 'report')
    evidence = read(records / 'evidence.json')
    need(isinstance(evidence, list), 'evidence must be a list')
    ids = set()
    for item in evidence:
        text_fields(item, ['id', 'kind', 'claim', 'source', 'checked_at', 'limitation'], 'evidence')
        need(item['id'] not in ids, 'Duplicate evidence ID')
        need(item['kind'] in ['fact', 'user', 'inference', 'hypothesis'], 'Invalid evidence kind')
        ids.add(item['id'])
    topics = []
    for folder in sorted((records / 'discussions').glob('*')):
        if not folder.is_dir():
            continue
        if not (folder / 'state.json').exists():
            raise ValueError(f'{folder.name}: missing state.json')
        state = read(folder / 'state.json')
        conclusion = read(folder / 'conclusion.json')
        text_fields(conclusion, ['id', 'title', 'status', 'recommendation', 'confidence', 'approval', 'next_action', 'dissent'], folder.name)
        need(conclusion['id'] == folder.name, 'Topic ID differs from directory')
        need(conclusion['status'] == state['status'], folder.name + ': status differs from runtime state')
        need(conclusion['approval'] in ['pending', 'approved', 'rejected'], 'Invalid approval')
        need(isinstance(conclusion.get('approval_evidence'), list), 'approval_evidence must be a list')
        need(set(conclusion['approval_evidence']) <= ids, 'Unknown approval evidence')
        if conclusion['approval'] != 'pending':
            need(any(e['id'] in conclusion['approval_evidence'] and e['kind'] == 'user' for e in evidence), 'User approval needs user evidence')
        for key in ['questions', 'unknowns', 'blockers']:
            need(isinstance(conclusion.get(key), list) and all(isinstance(x, str) for x in conclusion[key]), 'Missing text list: ' + key)
        alternatives = conclusion.get('alternatives', [])
        need(isinstance(alternatives, list), 'alternatives must be a list (empty when not judged)')
        rubric = conclusion.get('rubric', 'general')
        need(rubric == state.get('rubric', 'general'), 'Rubric differs from pre-debate declaration')
        need(rubric in RUBRICS, 'Unknown rubric')
        for alt in alternatives:
            text_fields(alt, ['name'], 'alternative')
            scores = alt.get('scores')
            need(isinstance(scores, list) and len(scores) == 5, 'Exactly five criterion scores required')
            for score in scores:
                value = score.get('value')
                need(value is None or (type(value) in (int, float) and 0 <= value <= 5), 'Score must be null or 0–5')
                text_fields(score, ['reason', 'limitation', 'revisit'], 'score')
                need(isinstance(score.get('evidence'), list) and set(score['evidence']) <= ids, 'Unknown score evidence')
                need(value is None or len(score['evidence']) > 0, 'Numeric score needs evidence references')
        need((folder / 'discussion.md').exists(), folder.name + ': missing transcript')
        topics.append(conclusion)
    need(topics, 'No topics to report')
    need(data.get('topic_ids') == [t['id'] for t in topics], 'Report topic IDs omit or reorder source topics')
    impacts = read(records / 'impacts.json')
    need(isinstance(impacts, list), 'impacts must be a list')
    for item in impacts:
        text_fields(item, ['decision', 'before', 'after', 'reason'], 'impact')
        need(isinstance(item.get('areas'), list) and item['areas'], 'Impact areas required')
        for area in item['areas']:
            text_fields(area, ['name', 'status', 'reason'], 'impact area')
            need(area['status'] in ['updated', 'retained', 'review_needed'], 'Invalid impact status')
    return root, data, topics, evidence, impacts


def fingerprint(root):
    digest = hashlib.sha256()
    for path in sorted((root / 'records').rglob('*')):
        if path.is_file() and path.suffix in ('.json', '.md') and path.name not in ('round.json', 'report-build.json'):
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def reader_fields(topic):
    """Reader summaries are authored from the discussion, never guessed from scores."""
    reader = topic.get('reader')
    need(isinstance(reader, dict), topic['id'] + ': reader summary required; rewrite from discussion, not scores')
    text_fields(reader, ['question', 'result', 'why', 'direction'], 'reader')
    conversation = reader.get('conversation')
    need(isinstance(conversation, list) and conversation, 'Reader needs a short account of the actual discussion')
    for turn in conversation:
        text_fields(turn, ['speaker', 'point'], 'conversation')
    for field in ['plan', 'ai_tasks', 'unfinished']:
        need(isinstance(reader.get(field), list) and all(isinstance(x, str) for x in reader[field]), 'Missing reader list: ' + field)
    questions = reader.get('feedback')
    need(isinstance(questions, list), 'feedback must be a list')
    for question in questions:
        text_fields(question, ['question', 'recommendation', 'why_user'], 'feedback')
        need(isinstance(question.get('options'), list) and len(question['options']) >= 2, 'Feedback needs understandable options')
        for option in question['options']:
            text_fields(option, ['label', 'effect'], 'feedback option')
    visuals = reader.get('visuals')
    need(isinstance(visuals, list), 'visuals must be a list')
    need(reader.get('kind') in ['general','design','engineering'], 'Reader kind required')
    if reader['kind'] in ['design','engineering']:
        need(visuals, 'Design/engineering conclusions need an inline screen or flow example')
    for visual in visuals:
        text_fields(visual, ['title', 'caption', 'type'], 'visual')
        if visual['type'] == 'flow':
            need(isinstance(visual.get('steps'), list) and len(visual['steps']) >= 2 and all(isinstance(x,str) for x in visual['steps']), 'Flow needs at least two labeled steps')
        elif visual['type'] == 'screen':
            text_fields(visual, ['screen_title'], 'screen')
            need(isinstance(visual.get('elements'),list) and visual['elements'], 'Screen needs elements')
            for element in visual['elements']:
                text_fields(element, ['type','label'], 'screen element')
                need(element['type'] in ['text','field','button','card'], 'Unsupported screen element')
        elif visual['type'] == 'image':
            text_fields(visual,['path','alt'], 'image')
        else:
            raise ValueError('Unknown visual type')
    return reader


def render(round_dir):
    root, data, topics, evidence, impacts = load(round_dir)
    esc = lambda value: html.escape(str(value), quote=True)
    readers = [(topic, reader_fields(topic)) for topic in topics]
    ul = lambda values: '<ul>' + ''.join('<li>' + esc(x) + '</li>' for x in values) + '</ul>'
    parts = [f'<header><p class="meta">PLANWITH · {esc(root.name)}</p><h1>{esc(data["title"])}</h1><p class="meta">{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</p></header>', f'<section><h2>이번에는 이렇게 정리함</h2><p class="summary lead">{esc(data["summary"])}</p></section>']
    meta = read(root/'records/round.json') if (root/'records/round.json').exists() else {}
    previous = meta.get('previous')
    if previous and re.fullmatch(r'round-\d{3,}', previous):
        parts.append('<p><a href="../'+esc(previous)+'/conclusion-report.html">지난 보고서</a></p>')
    parts.append('<nav aria-label="논의 주제"><h2>무슨 이야기를 했나</h2><ul>')
    for topic, reader in readers:
        parts.append('<li><a href="#'+esc(topic['id'])+'">'+esc(reader['question'])+'</a></li>')
    parts.append('</ul></nav>')
    for topic, reader in readers:
        label = {'pending':'두 AI의 제안 · 아직 사용자 확정 전', 'approved':'사용자가 정한 방향', 'rejected':'사용자가 채택하지 않은 제안'}[topic['approval']]
        parts.append(f'<section id="{esc(topic["id"])}"><p class="meta">{esc(label)}</p><h2>{esc(reader["question"])}</h2><h3>어떤 이야기가 오갔나</h3><div class="conversation">')
        for turn in reader['conversation']:
            parts.append('<div class="turn"><strong>'+esc(turn['speaker'])+'</strong><p>'+esc(turn['point'])+'</p></div>')
        parts.append('</div><div class="summary"><h3>그래서 나온 결론</h3><p class="lead">'+esc(reader['result'])+'</p><p>'+esc(reader['why'])+'</p></div>')
        parts.append('<h3>이렇게 진행하려 함</h3><p>'+esc(reader['direction'])+'</p>'+ul(reader['plan']))
        for visual in reader['visuals']:
            parts.append('<figure><h3>'+esc(visual['title'])+'</h3>')
            if visual['type']=='flow':
                parts.append('<ol class="flow">'+''.join('<li>'+esc(step)+'</li>' for step in visual['steps'])+'</ol>')
            elif visual['type']=='screen':
                parts.append('<div class="screen"><div class="screen-header">'+esc(visual['screen_title'])+'</div>')
                for element in visual['elements']:
                    parts.append('<div class="mock-'+esc(element['type'])+'">'+esc(element['label'])+'</div>')
                parts.append('</div><p class="note">화면 예시이며 실제 저장·결제 등은 실행되지 않음.</p>')
            else:
                path=(root/visual['path']).resolve()
                need(root in path.parents and path.is_file(), 'Image must exist inside the round folder')
                mime={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}.get(path.suffix.lower())
                need(mime, 'Use PNG, JPEG or WebP images')
                need(path.stat().st_size <= 10_000_000, 'Image exceeds 10 MB; reduce it before embedding')
                parts.append('<img alt="'+esc(visual['alt'])+'" src="data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()+'">')
            parts.append('<figcaption>'+esc(visual['caption'])+'</figcaption></figure>')
        parts.append('</section>')
    tasks=[task for _,r in readers for task in r['ai_tasks']]
    unfinished=[task for _,r in readers for task in r['unfinished']]
    if tasks:
        parts.append('<section><h2>AI가 이어서 할 일</h2>'+ul(tasks)+'</section>')
    if unfinished:
        parts.append('<section><h2>아직 끝내지 못한 것</h2>'+ul(unfinished)+'</section>')
    feedback=[q for _,r in readers for q in r['feedback']]
    parts.append('<section><h2>이 방향에 대한 의견을 듣고 싶음</h2>')
    if not feedback:
        parts.append('<p>지금 꼭 선택할 항목은 없음. 바꾸고 싶은 방향이나 더하고 싶은 의견을 대화에 남기면 다음 논의에 반영함.</p>')
    for question in feedback:
        parts.append('<h3>'+esc(question['question'])+'</h3><p>'+esc(question['recommendation'])+'</p><p class="note">'+esc(question['why_user'])+'</p>'+ul([o['label']+' — '+o['effect'] for o in question['options']]))
    parts.append('<p class="note">의견은 이 보고서를 받은 대화에 입력하면 됨. 제시한 선택지 외의 생각도 반영 가능함.</p></section>')
    if impacts:
        parts.append('<section><h2>지난번 의견을 이렇게 반영함</h2>')
        for impact in impacts:
            parts.append('<h3>'+esc(impact['decision'])+'</h3><p>'+esc(impact['before'])+' → '+esc(impact['after'])+'</p><p>'+esc(impact['reason'])+'</p>')
        parts.append('</section>')
    parts.append('<footer><details><summary>필요할 때만 보는 전체 기록</summary><ul>')
    for topic in topics:
        parts.append('<li><a href="records/discussions/'+esc(topic['id'])+'/discussion.md">'+esc(topic['title'])+' 논의 기록</a></li>')
    parts.append('</ul></details></footer>')
    template=(Path(__file__).resolve().parents[1]/'assets/conclusion-report.html').read_text(encoding='utf-8')
    css=template.split('<style>',1)[1].split('</style>',1)[0]
    output='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(data['title'])+'</title><style>'+css+'</style></head><body><main>'+''.join(parts)+'</main><!-- planwith-source:'+fingerprint(root)+' --></body></html>'
    (root/'conclusion-report.html').write_text(output,encoding='utf-8')
    (root/'records/report-build.json').write_text(json.dumps({'html_sha256': hashlib.sha256(output.encode()).hexdigest()}, indent=2), encoding='utf-8')
    return root/'conclusion-report.html'


def verify(round_dir):
    root, _, topics, _, _ = load(round_dir)
    for topic in topics:
        reader_fields(topic)
    expected='<!-- planwith-source:'+fingerprint(root)+' -->'
    need(expected in (root/'conclusion-report.html').read_text(encoding='utf-8'), 'Report stale: source records changed; regenerate')
    # Detect modifications after validated rendering; semantic source truth still needs review.
    original=(root/'conclusion-report.html').read_text(encoding='utf-8')
    need(hashlib.sha256(original.encode()).hexdigest() == read(root/'records/report-build.json')['html_sha256'], 'Report content changed after validated render; regenerate')
    return True


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action', choices=['render','verify'])
    parser.add_argument('--round', required=True, type=Path)
    args=parser.parse_args()
    try:
        print(render(args.round) if args.action=='render' else verify(args.round))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        sys.exit(str(exc))
