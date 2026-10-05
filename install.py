#!/usr/bin/env python3
"""Install shared skill without dependencies, symlinks, or destructive rule edits."""
import argparse
import os
from pathlib import Path
import shutil
import sys

START = '<!-- planwith:start -->'
END = '<!-- planwith:end -->'
OWNER = '.planwith-managed'
RULE = '''When the user asks to plan, debate, or review with Claude or Codex (including
"클로드랑 기획해봐", "코덱스랑 기획해봐"), apply the planwith skill.
Do not invoke peer agents when PLANWITH_PARTICIPANT=1. Follow the skill's bounded
rounds and user-input gates. Use official local CLIs only, never API fallback.'''


def edit_rule(path, remove=False):
    original = path.read_text(encoding='utf-8') if path.exists() else ''
    if original.count(START) != original.count(END) or original.count(START) > 1:
        raise ValueError(f'Malformed managed block: {path}')
    if START in original:
        a, b = original.index(START), original.index(END) + len(END)
        original = original[:a] + original[b:]
    result = original if remove else original.rstrip('\n') + '\n\n' + START + '\n' + RULE + '\n' + END + '\n'
    if path.exists() and not path.with_name(path.name + '.pre-planwith').exists():
        shutil.copy2(path, path.with_name(path.name + '.pre-planwith'))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result, encoding='utf-8')


def install(home=None, remove=False):
    home = Path(home or Path.home()).resolve()
    codex = Path(os.environ.get('CODEX_HOME', home / '.codex'))
    claude = Path(os.environ.get('CLAUDE_CONFIG_DIR', home / '.claude'))
    targets = [(codex / 'skills/planwith', codex / 'AGENTS.md'),
               (claude / 'skills/planwith', claude / 'CLAUDE.md')]
    # Preflight both destinations before changing either.
    for dest, rule in targets:
        if dest.exists() and (dest.is_symlink() or not (dest / OWNER).exists()):
            raise ValueError(f'Refusing to replace unmanaged skill: {dest}')
        contents = rule.read_text(encoding='utf-8') if rule.exists() else ''
        if contents.count(START) != contents.count(END) or contents.count(START) > 1:
            raise ValueError(f'Malformed managed block: {rule}')
    for dest, rule in targets:
        if dest.exists():
            shutil.rmtree(dest)
        if not remove:
            shutil.copytree(Path(__file__).parent / 'skill', dest,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            (dest / OWNER).write_text('planwith\n', encoding='utf-8')
        edit_rule(rule, remove)
        print(('Removed ' if remove else 'Installed ') + str(dest))
    if not remove:
        for cli in ('claude', 'codex'):
            print(f'{cli}: {shutil.which(cli) or "MISSING — install and sign in first"}')
        print('Open a new CLI session. No model calls were made. Requires Python 3.9+.')


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--uninstall', action='store_true')
    args = parser.parse_args()
    try:
        install(remove=args.uninstall)
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
