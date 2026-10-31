"""Fail packaging if runtime files or developer home paths enter a release."""
import marshal
from pathlib import Path
import re
import zipfile

from PyInstaller.archive.readers import CArchiveReader

root = Path(__file__).resolve().parent.parent
private_path = re.compile(rb'[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\x00]{2,}[\\/]', re.I)
with zipfile.ZipFile(root / 'release/RiotProfiles-Source.zip') as source:
    for name in source.namelist():
        path = Path(name)
        if path.suffix in ('.img', '.qcow2', '.log', '.pyc') or path.name in ('profiles.json', 'settings.json', 'adbkey', 'adbkey.pub', 'launcher-runtime.json'):
            raise RuntimeError('Runtime file in source archive: ' + name)
        if private_path.search(source.read(name)):
            raise RuntimeError('Developer home path in source archive: ' + name)
archive = CArchiveReader(str(root / 'release/RiotProfiles.exe'))
for name in archive.toc:
    if private_path.search(archive.extract(name)):
        raise RuntimeError('Developer home path in EXE entry: ' + name)
python = archive.open_embedded_archive('PYZ.pyz')
for name in python.toc:
    code = python.extract(name)
    if code is not None and private_path.search(marshal.dumps(code)):
        raise RuntimeError('Developer home path in Python module: ' + name)
print('Release privacy audit passed.')
