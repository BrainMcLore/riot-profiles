"""Download Android components from Google; never package user device data."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

from .core import IMAGE, atomic_json, locked, sdk_ready

GOOGLE = 'https://dl.google.com/android/repository/'
SOURCES = (
    (GOOGLE, 'repository2-1.xml', 'emulator', ''),
    (GOOGLE, 'repository2-1.xml', 'platform-tools', ''),
    (GOOGLE + 'sys-img/google_apis_playstore/', 'sys-img2-1.xml',
     IMAGE.replace('/', ';'), 'system-images/android-33/google_apis_playstore'),
)


@dataclass(frozen=True)
class Package:
    name: str
    url: str
    size: int
    digest: str
    algorithm: str
    destination: str
    license: str


def official_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname != 'dl.google.com' or not parsed.path.startswith('/android/repository/'):
        raise ValueError('Компоненты Android разрешено скачивать только с dl.google.com.')
    return url


def select_package(xml, name, base, destination):
    root = ET.fromstring(xml)
    candidates = [p for p in root.findall('remotePackage') if p.get('path') == name
                  and (p.find('channelRef') is None or p.find('channelRef').get('ref') == 'channel-0')
                  and p.find('revision/preview') is None]
    compatible = []
    for package in candidates:
        archives = [a.find('complete') for a in package.findall('archives/archive')
                    if a.findtext('host-os') in (None, 'windows')
                    and a.findtext('host-arch') in (None, 'x86_64')]
        if archives:
            compatible.append((package, archives[0]))
    if not compatible:
        raise RuntimeError('Google не предлагает нужный стабильный пакет: ' + name)
    package, archive = max(compatible, key=lambda pair: tuple(int(pair[0].findtext('revision/' + n, '0')) for n in ('major', 'minor', 'micro')))
    uses_license = package.find('uses-license')
    license_id = uses_license.get('ref') if uses_license is not None else None
    terms = next((''.join(node.itertext()) for node in root.findall('license') if node.get('id') == license_id), '')
    if not terms.strip():
        raise RuntimeError('Не найден текст лицензии Google для ' + name)
    checksum = archive.find('checksum')
    algorithm = checksum.get('type', 'sha1').replace('-', '').lower()
    if algorithm not in ('sha1', 'sha256'):
        raise ValueError('Неподдерживаемый алгоритм проверки пакета.')
    return Package(name, official_url(urllib.parse.urljoin(base, archive.findtext('url'))),
                   int(archive.findtext('size')), checksum.text.strip(), algorithm, destination, terms)


def plan_install():
    cache = {}
    packages = []
    for base, index, name, destination in SOURCES:
        url = official_url(base + index)
        if url not in cache:
            with urllib.request.urlopen(url, timeout=60) as response:
                official_url(response.url)
                cache[url] = response.read(20 * 1024 * 1024)
        packages.append(select_package(cache[url], name, base, destination))
    return packages


def hash_file(path, algorithm='sha256'):
    digest = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def safe_extract(archive, destination):
    destination = destination.resolve()
    with zipfile.ZipFile(archive) as source:
        # Validate the whole archive before extracting anything.
        for entry in source.infolist():
            path = (destination / entry.filename).resolve()
            if not path.is_relative_to(destination) or '\\' in entry.filename or ':' in entry.filename:
                raise ValueError('Небезопасный путь внутри ZIP.')
            if (entry.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Символические ссылки внутри ZIP не поддерживаются.')
        source.extractall(destination)


def download(package, path, progress):
    if path.exists() and path.stat().st_size == package.size and hash_file(path, package.algorithm) == package.digest:
        return
    partial = path.with_suffix('.part')
    with urllib.request.urlopen(official_url(package.url), timeout=120) as response:
        official_url(response.url)
        with partial.open('wb') as output:
            downloaded = 0
            while chunk := response.read(2 * 1024 * 1024):
                output.write(chunk)
                downloaded += len(chunk)
                if downloaded > package.size:
                    raise ValueError('Размер загрузки превысил размер из каталога Google.')
                progress(f'{package.name}: {downloaded // 1048576} / {package.size // 1048576} МБ')
    if partial.stat().st_size != package.size or hash_file(partial, package.algorithm) != package.digest:
        raise ValueError('Контрольная сумма пакета не совпала. Повтори установку.')
    partial.replace(path)


def install_sdk(paths, packages, accepted, progress=print):
    if not accepted:
        raise ValueError('Необходимо принять лицензии скачиваемых компонентов Google.')
    paths.root.mkdir(parents=True, exist_ok=True)
    with locked(paths.root / 'setup.lock'):
        if sdk_ready(paths):
            progress('Компоненты Android уже установлены.')
            return
        if shutil.disk_usage(paths.root).free < 15 * 1024 ** 3:
            raise RuntimeError('Нужно минимум 15 ГБ свободного места для установки и первого профиля.')
        cache = paths.root / 'downloads'
        cache.mkdir(exist_ok=True)
        for package in packages:
            archive = cache / Path(urllib.parse.urlparse(package.url).path).name
            download(package, archive, progress)
            progress('Распаковка: ' + package.name)
            stage_parent = paths.root / 'staging'
            stage_parent.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='package-', dir=stage_parent) as temporary:
                stage = Path(temporary)
                safe_extract(archive, stage)
                entries = list(stage.iterdir())
                if len(entries) != 1 or not entries[0].is_dir():
                    raise ValueError('Неожиданная структура ZIP от Google.')
                source = entries[0]
                expected = 'x86_64' if package.name.startswith('system-images;') else package.name
                if source.name != expected:
                    raise ValueError('Неожиданная папка пакета: ' + source.name)
                destination = paths.sdk / package.destination / source.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    # Only replace incomplete SDK packages inside this app's private SDK.
                    if not destination.resolve().is_relative_to(paths.sdk.resolve()):
                        raise ValueError('Каталог SDK находится за пределами установки.')
                    shutil.rmtree(destination)
                shutil.move(str(source), str(destination))
        if not sdk_ready(paths):
            raise RuntimeError('Установка неполная. Повтори установку компонентов.')
        atomic_json(paths.root / 'sdk-install.json', {'packages': [
            {'name': p.name, 'url': p.url, 'digest': p.digest, 'algorithm': p.algorithm,
             'accepted_license_sha256': hashlib.sha256(p.license.encode()).hexdigest()} for p in packages]})
        for index, package in enumerate(packages):
            license_dir = paths.root / 'licenses'
            license_dir.mkdir(exist_ok=True)
            (license_dir / f'google-{index + 1}.txt').write_text(package.license, encoding='utf-8')
        progress('Android готов. Создай профиль и запусти его.')
