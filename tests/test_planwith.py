import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def test_reinstall_and_remove_preserve_rules(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            home = Path(tmp)
            rule = home / '.codex/AGENTS.md'
            rule.parent.mkdir()
            rule.write_text('User rules\n', encoding='utf-8')
            installer.install(home)
            installer.install(home)
            self.assertEqual(rule.read_text(encoding="utf-8").count(installer.START), 1)
            self.assertIn('User rules', rule.read_text(encoding="utf-8"))
            installer.install(home, remove=True)
            self.assertIn('User rules', rule.read_text(encoding="utf-8"))
            self.assertNotIn(installer.START, rule.read_text(encoding="utf-8"))
            self.assertFalse((home / '.claude/skills/planwith').exists())

    def test_unmanaged_skill_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            dest = Path(tmp) / '.claude/skills/planwith'
            dest.mkdir(parents=True)
            with self.assertRaises(ValueError):
                installer.install(tmp)
            self.assertFalse((Path(tmp) / '.codex/skills/planwith').exists())


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = os.environ.copy()
        self.env.pop('PLANWITH_PARTICIPANT', None)

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args, topic='docs/test/001'):
        return subprocess.run([sys.executable, str(ROOT / 'skill/scripts/peer.py'),
                               '--project', str(self.root), '--topic', topic, *args],
                              env=self.env, capture_output=True, text=True)

    def test_pause_answer_and_no_reset(self):
        self.assertEqual(self.cli('init', '--title', 'Target').returncode, 0)
        self.assertNotEqual(self.cli('init', '--title', 'Reset').returncode, 0)
        self.assertEqual(self.cli('pause', '--question', 'Who pays?').returncode, 0)
        self.assertNotEqual(self.cli('call', '--provider', 'claude', '--phase', 'proposal', '--prompt-file', 'missing').returncode, 0)
        answer = self.root / 'answer.txt'
        answer.write_text('Small businesses', encoding='utf-8')
        self.assertEqual(self.cli('answer', '--file', str(answer)).returncode, 0)
        state = json.loads(self.cli('status').stdout)
        self.assertEqual(state['status'], 'active')
        self.assertIn('Small businesses', (self.root / 'docs/test/001/discussion.md').read_text(encoding="utf-8"))
        self.assertEqual(self.cli('finish', '--reason', 'Needs validation').returncode, 0)
        self.assertNotEqual(self.cli('answer', '--file', str(answer)).returncode, 0)

    def test_path_escape_and_recursion(self):
        self.assertNotEqual(self.cli('init', '--title', 'Escape', topic='../outside').returncode, 0)
        self.env['PLANWITH_PARTICIPANT'] = '1'
        self.assertNotEqual(self.cli('init', '--title', 'Nested').returncode, 0)

    def test_budget_and_phase_limits(self):
        self.cli('init', '--title', 'Limits')
        path = self.root / 'docs/test/001/state.json'
        state = json.loads(path.read_text(encoding="utf-8"))
        state['calls'] = [{'phase': 'proposal'}] * 8
        path.write_text(json.dumps(state))
        result = self.cli('call', '--provider', 'codex', '--phase', 'judge', '--prompt-file', 'missing')
        self.assertIn('budget exhausted', result.stderr)
        state['calls'] = []
        state['last_phase'] = 3
        path.write_text(json.dumps(state))
        result = self.cli('call', '--provider', 'codex', '--phase', 'proposal', '--prompt-file', 'missing')
        self.assertIn('earlier phase', result.stderr)


if __name__ == '__main__':
    unittest.main()

class ProcessTests(unittest.TestCase):
    def test_timeout_kills_child(self):
        spec = importlib.util.spec_from_file_location('peer', ROOT / 'skill/scripts/peer.py')
        peer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(peer)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(subprocess.TimeoutExpired):
                peer.run([sys.executable, '-c', 'import time; time.sleep(10)'], '', tmp, os.environ.copy(), .1)

    def test_success_is_appended_and_accounted(self):
        spec = importlib.util.spec_from_file_location('peer', ROOT / 'skill/scripts/peer.py')
        peer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(peer)
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            root = Path(tmp)
            base = ['peer.py', '--project', tmp, '--topic', 'docs/test']
            with patch.object(sys, 'argv', base + ['init', '--title', 'Example']):
                peer.main()
            prompt = root / 'prompt.txt'
            prompt.write_text('Review the proposal', encoding='utf-8')
            auth = subprocess.CompletedProcess([], 0, '{"authMethod":"claude.ai","loggedIn":true}', '')
            with patch.object(sys, 'argv', base + ['call', '--provider', 'claude', '--phase', 'proposal', '--prompt-file', str(prompt)]), patch.object(peer.shutil, 'which', return_value='claude'), patch.object(peer.subprocess, 'run', return_value=auth), patch.object(peer, 'run', return_value='Claim A-01: needs customer evidence.'):
                peer.main()
            state = json.loads((root / 'docs/test/state.json').read_text(encoding="utf-8"))
            self.assertEqual(len(state['calls']), 1)
            self.assertEqual(state['calls'][0]['status'], 'completed')
            self.assertIn('Claim A-01', (root / 'docs/test/discussion.md').read_text(encoding="utf-8"))
