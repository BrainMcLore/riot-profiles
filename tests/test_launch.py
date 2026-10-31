from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from app import core


class LaunchTests(unittest.TestCase):
    @patch('app.core.port_open', return_value=True)
    @patch('app.core.sdk_ready', return_value=True)
    @patch('app.core.running_port', return_value=None)
    @patch('app.core.free_emulator_port', return_value=5562)
    @patch('app.core.subprocess.Popen')
    def test_new_profile_launch_uses_own_avd_and_port(self, popen, *_):
        popen.return_value.pid = 999
        with tempfile.TemporaryDirectory() as temporary:
            paths = core.Paths(Path(temporary))
            profile = core.Profiles(paths).create('Example')
            port, started = core.start_profile(paths, profile, cold=True)
            self.assertEqual((port, started), (5562, True))
            args = popen.call_args.args[0]
            self.assertIn('rp_' + profile['id'], args)
            self.assertIn('-no-snapshot-load', args)
            self.assertNotIn('-wipe-data', args)
            self.assertEqual(popen.call_args.kwargs['env']['ANDROID_AVD_HOME'], str(paths.avds))
            self.assertTrue((paths.data / 'android').is_dir())

    @patch('app.core.sdk_ready', return_value=True)
    @patch('app.core.running_port', return_value=5562)
    @patch('app.core.subprocess.Popen')
    def test_running_profile_is_reused(self, popen, *_):
        with tempfile.TemporaryDirectory() as temporary:
            paths = core.Paths(Path(temporary))
            profile = core.Profiles(paths).create('Example')
            self.assertEqual(core.start_profile(paths, profile), (5562, False))
            popen.assert_not_called()

    @patch('app.core.adb')
    def test_rejects_commands_to_wrong_profile(self, adb):
        adb.side_effect = [Mock(stdout=b'', returncode=0), Mock(stdout=b'1', returncode=0),
                           Mock(stdout=b'rp_OTHER', returncode=0)]
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, 'другим'):
                core.wait_ready(core.Paths(Path(temporary)), {'id': 'a' * 32}, 5562)
