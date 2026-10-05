import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skill/scripts'
sys.path.insert(0, str(SCRIPTS))
from rounds import manage

class RoundTests(unittest.TestCase):
    def test_lifecycle_preserves_previous_documents(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = manage(tmp, 'docs', 'new', 'Initial idea')
            report = first / 'conclusion-report.html'
            report.write_text('Historical report', encoding='utf-8')
            self.assertEqual(first, manage(tmp, 'docs', 'resume'))
            with self.assertRaises(ValueError):
                manage(tmp, 'docs', 'new', 'Unauthorized reset')
            manage(tmp, 'docs', 'close')
            with self.assertRaises(ValueError):
                manage(tmp, 'docs', 'resume')
            second = manage(tmp, 'docs', 'new', 'User changed target')
            self.assertEqual(second.name, 'round-002')
            self.assertEqual(report.read_text(), 'Historical report')
            self.assertFalse((second / 'conclusion-report.html').exists())
            self.assertIn('round-001/conclusion-report.html', (Path(tmp)/'docs/planwith-rounds.md').read_text(encoding='utf-8'))

    def test_custom_base_and_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = manage(tmp, 'plans', 'new', 'Explicit custom base')
            self.assertEqual(result.parent.name, 'plans')
            with self.assertRaises(ValueError):
                manage(tmp, '../elsewhere', 'new', 'Escape')
