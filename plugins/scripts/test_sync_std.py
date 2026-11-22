import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync_std


class StdSyncTests(unittest.TestCase):
    def test_every_copy_matches_master(self):
        master = sync_std.master_path()
        self.assertEqual(sync_std.check(master, sync_std.version_of(master)), [])

    def test_stale_versions_are_detected_and_rewritten_for_any_version(self):
        ver = '1.7.0'
        text = ('STD-OKF-001-v1.2.0-stable, STD-OKF-001 v1.3.0-stable, '
                'y `v1.4.0-stable` suelto. Vigente: STD-OKF-001-v1.7.0-stable.')
        self.assertEqual(sync_std.stale_versions(text, ver), ['1.2.0', '1.3.0', '1.4.0'])
        new = sync_std.refresh_versions(text, ver)
        self.assertEqual(sync_std.stale_versions(new, ver), [])
        self.assertIn('STD-OKF-001-v1.7.0-stable, STD-OKF-001 v1.7.0-stable', new)
        self.assertIn('`v1.7.0-stable` suelto', new)
        self.assertIn('STD-OKF-001-v1.7.0-stable.', new)

    def test_current_version_is_left_untouched(self):
        text = 'Ver STD-OKF-001-v1.7.0-stable y v1.7.0-stable.'
        self.assertEqual(sync_std.stale_versions(text, '1.7.0'), [])
        self.assertEqual(sync_std.refresh_versions(text, '1.7.0'), text)

    def test_check_reports_stale_reference_in_a_plugin_file(self):
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'x-plugin' / 'docs').mkdir(parents=True)
            (root / 'x-plugin' / 'docs' / 'guia.md').write_text('Usa STD-OKF-001-v1.2.0-stable.', encoding='utf-8')
            master = root / 'STD-OKF-001-v1.7.0-stable.md'
            master.write_text('maestro', encoding='utf-8')
            with mock.patch.object(sync_std, 'PLUGINS', root):
                problems = sync_std.check(master, '1.7.0')
            self.assertTrue(any('referencia a versión anterior 1.2.0' in p for p in problems), problems)


if __name__ == '__main__':
    unittest.main()
