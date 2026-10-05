#!/usr/bin/env python3
"""Create explicit planning rounds without mutating previous deliverables."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
from peer import lock, save


def manage(project, output, action, reason=''):
    if os.environ.get('PLANWITH_PARTICIPANT') == '1':
        raise ValueError('Participants cannot create planning rounds.')
    project = Path(project).resolve(strict=True)
    root = (project / output).resolve()
    if root == project or project not in root.parents:
        raise ValueError('Output must be a subdirectory of the host project.')
    root.mkdir(parents=True, exist_ok=True)
    with lock(root):
        rounds = sorted((p for p in root.iterdir() if p.is_dir() and re.fullmatch(r'round-\d{3,}', p.name)), key=lambda p: int(p.name[6:]))
        current = rounds[-1] if rounds else None
        if action == 'new':
            if not reason.strip():
                raise ValueError('A user-requested new round needs a recorded purpose.')
            if current:
                previous = json.loads((current / 'round.json').read_text(encoding='utf-8'))
                if previous['status'] != 'closed':
                    raise ValueError('Resume the current round or close it before starting another.')
            number = int(current.name[6:]) + 1 if current else 1
            target = root / f'round-{number:03d}'
            target.mkdir()
            save(target / 'round.json', {'number': number, 'status': 'active', 'purpose': reason,
                                        'previous': current.name if current else None})
            current = target
        elif action == 'close':
            if not current:
                raise ValueError('No planning round exists.')
            state = json.loads((current / 'round.json').read_text(encoding='utf-8'))
            state['status'] = 'closed'
            save(current / 'round.json', state)
        elif action == 'resume':
            if not current:
                raise ValueError('No planning round exists; create the first round.')
            if json.loads((current / 'round.json').read_text(encoding='utf-8'))['status'] != 'active':
                raise ValueError('Latest round is closed; request a new planning round.')
        # Separate managed index; never overwrite a user's docs/README.md.
        rounds = sorted((p for p in root.iterdir() if p.is_dir() and re.fullmatch(r'round-\d{3,}', p.name)), key=lambda p: int(p.name[6:]))
        lines = ['# Planwith 기획 라운드', '', '현재 라운드: ' + (current.name if current else '없음'), '']
        for folder in rounds:
            info = json.loads((folder / 'round.json').read_text(encoding='utf-8'))
            lines.append(f'- {folder.name} ({info["status"]})')
            for filename, label in [('README.md','기획 목차'),('conclusion-report.html','결론 보고서')]:
                if (folder / filename).exists():
                    lines.append(f'  - [{label}]({folder.name}/{filename})')
        (root / 'planwith-rounds.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return current


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', default='docs')
    parser.add_argument('action', choices=['new', 'resume', 'close', 'status'])
    parser.add_argument('--reason', default='')
    args = parser.parse_args()
    try:
        print(manage(args.project, args.output, args.action, args.reason))
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
