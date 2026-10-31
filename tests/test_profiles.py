import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.core import Paths, Profiles, environment


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.paths = Paths(Path(self.temp.name))
        self.manager = Profiles(self.paths)

    def test_profiles_are_fresh_and_keep_separate_data(self):
        first = self.manager.create('Первый аккаунт')
        first_dir = self.manager.avd(first)
        (first_dir / 'private-account.txt').write_text('SECRET-SENTINEL')
        second = self.manager.create('Второй аккаунт')
        second_dir = self.manager.avd(second)
        self.assertNotEqual(first_dir, second_dir)
        self.assertFalse((second_dir / 'private-account.txt').exists())
        for profile in (first, second):
            config = (self.manager.avd(profile) / 'config.ini').read_text()
            self.assertIn(profile['id'], config)
            self.assertIn(str(self.paths.sdk), config)
        self.assertNotIn('SECRET-SENTINEL', self.paths.index.read_text())

    def test_rename_preserves_identity_and_userdata(self):
        profile = self.manager.create('Old')
        data = self.manager.avd(profile) / 'userdata-qemu.img'
        data.write_bytes(b'unchanged')
        self.manager.rename(profile['id'], 'New')
        self.assertEqual(self.manager.load(), [{'id': profile['id'], 'name': 'New'}])
        self.manager.initialize(self.manager.get(profile['id']))
        self.assertEqual(data.read_bytes(), b'unchanged')

    def test_rejects_duplicate_names_and_invalid_ids(self):
        self.manager.create('Main')
        with self.assertRaises(ValueError):
            self.manager.create('main')
        with self.assertRaises(ValueError):
            self.manager.avd({'id': '../../other'})
        for name in ('', '   ', 'foo\nbar', 'a' * 65):
            with self.assertRaises(ValueError):
                self.manager.create(name)

    def test_no_artificial_profile_limit(self):
        for index in range(70):
            self.manager.create('Profile ' + str(index))
        self.assertEqual(len(self.manager.load()), 70)

    @patch('app.core.running_port', return_value=None)
    def test_delete_only_selected_profile(self, _):
        first, second = self.manager.create('First'), self.manager.create('Second')
        self.manager.delete(first['id'])
        self.assertFalse(self.manager.avd(first).exists())
        self.assertTrue(self.manager.avd(second).exists())
        self.assertEqual(self.manager.load(), [second])

    @patch('app.core.running_port', return_value=5554)
    def test_cannot_delete_running_profile(self, _):
        profile = self.manager.create('Running')
        with self.assertRaises(RuntimeError):
            self.manager.delete(profile['id'])
        self.assertTrue(self.manager.avd(profile).exists())

    def test_corrupt_index_is_not_overwritten(self):
        self.paths.index.parent.mkdir(parents=True)
        self.paths.index.write_text('{bad JSON')
        with self.assertRaises(json.JSONDecodeError):
            self.manager.create('Do not reset')
        self.assertEqual(self.paths.index.read_text(), '{bad JSON')

    def test_environment_uses_only_new_app_paths(self):
        env = environment(self.paths)
        self.assertEqual(env['ANDROID_AVD_HOME'], str(self.paths.avds))
        self.assertEqual(env['ANDROID_ADB_SERVER_PORT'], '5041')


if __name__ == '__main__':
    unittest.main()
