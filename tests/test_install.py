from pathlib import Path
import tempfile
import unittest
import zipfile

from app.install import official_url, safe_extract, select_package


def package(revision, channel='channel-0', host='windows', preview=''):
    return f'''<remotePackage path="emulator"><revision><major>{revision}</major>{preview}</revision>
    <channelRef ref="{channel}"/><uses-license ref="terms"/>
    <archives><archive><host-os>{host}</host-os><host-arch>x86_64</host-arch><complete>
    <size>123</size><checksum type="sha-256">{'a' * 64}</checksum><url>emulator-{revision}.zip</url>
    </complete></archive></archives></remotePackage>'''


class InstallTests(unittest.TestCase):
    def test_chooses_highest_stable_windows_version(self):
        xml = ('<repository><license id="terms">Official license</license>' +
               package(1) + package(2) + package(99, 'channel-1') +
               package(100, preview='<preview>1</preview>') + package(101, host='linux') + '</repository>')
        result = select_package(xml, 'emulator', 'https://dl.google.com/android/repository/', '')
        self.assertEqual(result.algorithm, 'sha256')
        self.assertEqual(result.license, 'Official license')
        self.assertEqual(result.size, 123)
        # Latest compatible revision is selected even when a newer Linux-only build exists.
        self.assertTrue(result.url.endswith('emulator-2.zip'))

    def test_requires_license_text(self):
        with self.assertRaises(RuntimeError):
            select_package('<repository>' + package(1) + '</repository>', 'emulator',
                           'https://dl.google.com/android/repository/', '')

    def test_rejects_external_or_plain_http_urls(self):
        for url in ('http://dl.google.com/android/repository/a.zip',
                    'https://example.com/a.zip', 'https://dl.google.com.evil.test/android/repository/a.zip'):
            with self.assertRaises(ValueError):
                official_url(url)

    def test_zip_traversal_is_rejected_before_any_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'bad.zip'
            with zipfile.ZipFile(archive, 'w') as output:
                output.writestr('safe.txt', 'not extracted either')
                output.writestr('../private.txt', 'bad')
            with self.assertRaises(ValueError):
                safe_extract(archive, root / 'out')
            self.assertFalse((root / 'private.txt').exists())
            self.assertFalse((root / 'out/safe.txt').exists())

    def test_valid_package_extracts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'good.zip'
            with zipfile.ZipFile(archive, 'w') as output:
                output.writestr('emulator/test.txt', 'good')
            safe_extract(archive, root / 'out')
            self.assertEqual((root / 'out/emulator/test.txt').read_text(), 'good')
