"""Create an allowlisted source ZIP, never walking outside this repository."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent.parent
paths = [root / name for name in (
    'main.py', 'LICENSE', '.gitignore', 'README.md', 'THIRD_PARTY.md', 'PRIVACY.md',
    'requirements-build.txt', 'build.ps1', 'install.ps1', 'uninstall.ps1')]
paths.extend(root.glob('README.*.md'))
for folder in ('app', 'tests', 'tools', '.github', 'assets', 'docs'):
    paths.extend(path for path in (root / folder).rglob('*')
                 if path.is_file() and '__pycache__' not in path.parts
                 and path.suffix in ('.py', '.yml', '.ico', '.svg', '.txt', '.md'))
destination = root / 'release/RiotProfiles-Source.zip'
destination.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(set(paths)):
        if not path.resolve().is_relative_to(root):
            raise ValueError('Source path escapes repository')
        archive.write(path, Path('riot-profiles') / path.relative_to(root))
print(destination)
