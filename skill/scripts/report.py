#!/usr/bin/env python3
"""Validate structured conclusions and render a portable, escaped HTML report."""
import argparse
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
        alternatives = conclusion.get('alternatives')
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


def render(round_dir):
    root, data, topics, evidence, impacts = load(round_dir)
    esc = lambda value: html.escape(str(value), quote=True)
    ul = lambda values: '<ul>' + ''.join('<li>' + esc(x) + '</li>' for x in values) + '</ul>' if values else '<p class="note">해당 사항 없음</p>'
    table = lambda headers, rows: '<div class="table-wrap"><table><thead><tr>' + ''.join('<th>' + esc(x) + '</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join('<td>' + cell + '</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table></div>'
    approval = {'pending':'사용자 미확정', 'approved':'사용자 승인', 'rejected':'사용자 기각'}
    status = {'active':'논의 중', 'waiting_for_user':'사용자 입력 대기', 'finished':'논의 종료'}
    parts = [f'<header><p class="meta">PLANWITH · {esc(root.name)}</p><h1>{esc(data["title"])}</h1><p class="meta">갱신: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</p></header>', f'<section><h2>핵심 결론</h2><p class="summary">{esc(data["summary"])}</p></section>']
    meta = read(root/'records/round.json') if (root/'records/round.json').exists() else {}
    previous = meta.get('previous')
    if previous and re.fullmatch(r'round-\d{3,}', previous):
        parts.append('<p><a href="../'+esc(previous)+'/conclusion-report.html">이전 라운드 보고서</a></p>')
    parts += ['<section><h2>이번에 결정할 것</h2>' + ul([q for t in topics for q in t['questions']]) + '</section>', '<section><h2>아직 모르는 것</h2>' + ul([q for t in topics for q in t['unknowns']]) + '</section>']
    rows = [[esc(t['title']), esc(t['recommendation']), esc(status.get(t['status'],t['status'])),esc(approval[t['approval']])] for t in topics]
    parts.append('<section><h2>전체 안건</h2>' + table(['안건','권고','진행 상태','사용자 결정'], rows) + '</section>')
    parts.append('<section><h2>지난 라운드와 달라진 것</h2>')
    if not impacts:
        parts.append('<p>첫 라운드 또는 변경 사항 없음.</p>')
    for impact in impacts:
        parts.append(f'<h3>{esc(impact["decision"])}</h3><p>{esc(impact["before"])} → {esc(impact["after"])}</p><p>{esc(impact["reason"])}</p>')
        labels = {'updated':'갱신 완료','retained':'유지 근거 있음','review_needed':'재검토 필요'}
        parts.append(table(['영향 범위','상태','이유'],[[esc(a['name']),labels[a['status']],esc(a['reason'])] for a in impact['areas']]))
    parts.append('</section>')
    for topic in topics:
        parts.append(f'<section id="{esc(topic["id"])}"><h2>{esc(topic["title"])}</h2><p class="lead">{esc(topic["recommendation"])}</p><p>확신도: {esc(topic["confidence"])} · {approval[topic["approval"]]}</p>')
        weights = RUBRICS[topic.get('rubric','general')]
        for alt in topic['alternatives']:
            parts.append('<h3>' + esc(alt['name']) + '</h3>')
            rows=[]
            for criterion, weight, score in zip(CRITERIA, weights, alt['scores']):
                value=score['value']
                visual='판단 불가' if value is None else f'<meter min="0" max="5" value="{value}" aria-label="{esc(criterion)} {value}점"></meter> {value}/5'
                rows.append([esc(criterion)+f' ({weight}%)', visual, esc(score['reason']),esc(', '.join(score['evidence'])),esc(score['limitation']+' / 재검토: '+score['revisit'])])
            parts.append(table(['기준·비중','점수','근거','근거 ID','한계·재검토'],rows))
            values=[s['value'] for s in alt['scores']]
            total='판단 불가 항목으로 총점 미산출' if any(v is None for v in values) else f'가중 점수: {sum(v*w/5 for v,w in zip(values,weights)):.1f}/100'
            parts.append('<p class="note">'+total+' · 점수는 검토 판단이며 성공 확률이 아님.</p>')
        parts.append('<h3>필수 조건</h3>'+ul(topic['blockers'])+ '<p>남은 이견: '+esc(topic['dissent'])+'</p><p>다음 행동: '+esc(topic['next_action'])+'</p>')
        parts.append(f'<details><summary>상세 논의 기록</summary><a href="records/discussions/{esc(topic["id"])}/discussion.md">안건 원문</a></details></section>')
    parts.append('<section><h2>근거 목록</h2>'+table(['ID·유형','주장','출처·확인일','한계'],[[esc(e['id']+' · '+e['kind']),esc(e['claim']),esc(e['source']+' · '+e['checked_at']),esc(e['limitation'])] for e in evidence])+'</section>')
    template=(Path(__file__).resolve().parents[1]/'assets/conclusion-report.html').read_text(encoding='utf-8')
    css=template.split('<style>',1)[1].split('</style>',1)[0]
    output='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(data['title'])+'</title><style>'+css+'</style></head><body><main>'+''.join(parts)+'</main><!-- planwith-source:'+fingerprint(root)+' --></body></html>'
    (root/'conclusion-report.html').write_text(output,encoding='utf-8')
    (root/'records/report-build.json').write_text(json.dumps({'html_sha256': hashlib.sha256(output.encode()).hexdigest()}, indent=2), encoding='utf-8')
    return root/'conclusion-report.html'


def verify(round_dir):
    root, *_ = load(round_dir)
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
