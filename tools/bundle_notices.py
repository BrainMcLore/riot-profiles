"""Collect redistribution notices from the build runtime, without build paths."""
import importlib.metadata
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
sections = []
python_license = Path(sys.base_prefix) / 'LICENSE.txt'
if not python_license.is_file():
    raise RuntimeError('Python license file not found')
sections.append('PYTHON RUNTIME\n\n' + python_license.read_text(encoding='utf-8'))
distribution = importlib.metadata.distribution('pyinstaller')
for item in distribution.files or []:
    if str(item).lower().endswith('licenses/copying.txt'):
        sections.append('PYINSTALLER BOOTLOADER\n\n' + distribution.locate_file(item).read_text(encoding='utf-8'))
for item in sorted((Path(sys.base_prefix) / 'tcl').glob('*/license.terms')):
    sections.append('TCL / TK\n\n' + item.read_text(encoding='utf-8'))
if len(sections) < 3:
    raise RuntimeError('Missing Python, PyInstaller or Tcl/Tk notices')
(root / 'assets/THIRD_PARTY_LICENSES.txt').write_text('\n\n'.join(sections), encoding='utf-8')
