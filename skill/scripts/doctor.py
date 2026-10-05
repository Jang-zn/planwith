#!/usr/bin/env python3
"""Read-only compatibility and subscription checks. No model calls or secrets in output."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

OVERRIDES = ('ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'OPENAI_API_KEY', 'CODEX_API_KEY',
             'ANTHROPIC_BASE_URL', 'OPENAI_BASE_URL', 'CLAUDE_CODE_USE_BEDROCK',
             'CLAUDE_CODE_USE_VERTEX', 'CLAUDE_CODE_USE_FOUNDRY')


def inspect(project):
    result = {'project': str(Path(project).resolve()), 'checks': []}
    def check(name, ok, detail):
        result['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
    check('python', sys.version_info >= (3, 9), 'Python 3.9+ required')
    check('project', Path(project).is_dir(), 'Existing host working directory required')
    active = [key for key in OVERRIDES if os.environ.get(key)]
    check('subscription_environment', not active, 'Unset overrides: ' + ', '.join(active) if active else 'No API/provider environment overrides')
    for provider in ('claude', 'codex'):
        binary = shutil.which(provider)
        if not binary:
            check(provider, False, 'CLI missing; install official CLI and sign in'); continue
        try:
            version = subprocess.run([binary, '--version'], capture_output=True, text=True, encoding='utf-8', timeout=15)
            check(provider + '_version', version.returncode == 0, version.stdout.strip()[:100])
            args = ['exec', '--help'] if provider == 'codex' else ['--help']
            help_result = subprocess.run([binary] + args, capture_output=True, text=True, encoding='utf-8', timeout=15)
            required = ['--ignore-user-config', '--ephemeral', '--sandbox'] if provider == 'codex' else ['--strict-mcp-config', '--tools', '--setting-sources', '--no-session-persistence']
            missing = [flag for flag in required if flag not in help_result.stdout]
            check(provider + '_options', not missing and help_result.returncode == 0, 'Missing: ' + ', '.join(missing) if missing else 'Required options available')
            auth_args = ['login', 'status'] if provider == 'codex' else ['auth', 'status']
            auth = subprocess.run([binary] + auth_args, capture_output=True, text=True, encoding='utf-8', timeout=15)
            if provider == 'codex':
                ok = auth.returncode == 0 and 'ChatGPT' in auth.stdout + auth.stderr
            else:
                info = json.loads(auth.stdout) if auth.returncode == 0 else {}
                ok = info.get('loggedIn') and info.get('authMethod') == 'claude.ai'
            check(provider + '_subscription', ok, 'Subscription login verified' if ok else 'Sign in with subscription; API fallback disabled')
        except (OSError, ValueError, subprocess.TimeoutExpired):
            check(provider, False, 'CLI check failed or timed out; run official CLI manually')
    result['ok'] = all(item['ok'] for item in result['checks'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', default='.')
    args = parser.parse_args()
    result = inspect(args.project)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    sys.exit(0 if result['ok'] else 1)
