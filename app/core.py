from contextlib import contextmanager
from dataclasses import dataclass
import json
import os
from pathlib import Path
import socket
import shutil
import subprocess
import time
import uuid

VERSION = '0.2.0'
AVD_PREFIX = 'rp_'
ADB_PORT = 5041
IMAGE = 'system-images/android-33/google_apis_playstore/x86_64'
PACKAGE = 'com.riotgames.mobile.leagueconnect'
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


@dataclass(frozen=True)
class Paths:
    root: Path

    @classmethod
    def default(cls):
        return cls((Path(os.environ['LOCALAPPDATA']) / 'RiotProfiles').resolve())

    @property
    def sdk(self):
        return self.root / 'sdk'

    @property
    def data(self):
        return self.root / 'data'

    @property
    def avds(self):
        return self.data / 'avd'

    @property
    def index(self):
        return self.data / 'profiles.json'


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def locked(path):
    """Serialize profile updates and launches across launcher processes."""
    import msvcrt
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b'0')
            stream.flush()
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)


class Profiles:
    def __init__(self, paths):
        self.paths = paths

    def load(self):
        if not self.paths.index.exists():
            return []
        value = json.loads(self.paths.index.read_text(encoding='utf-8'))
        if value.get('schema') != 1 or not isinstance(value.get('profiles'), list):
            raise ValueError('Неподдерживаемый формат profiles.json. Данные не изменены.')
        profiles = value['profiles']
        ids = set()
        for profile in profiles:
            self.validate_id(profile['id'])
            self.validate_name(profile['name'])
            if profile['id'] in ids:
                raise ValueError('Повторяющийся ID профиля. Данные не изменены.')
            ids.add(profile['id'])
        return profiles

    @staticmethod
    def validate_id(value):
        if not isinstance(value, str) or len(value) != 32 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('Некорректный ID профиля.')
        return value

    @staticmethod
    def validate_name(value):
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 64 or any(ord(c) < 32 for c in value):
            raise ValueError('Название должно содержать от 1 до 64 символов без переносов строк.')
        return value.strip()

    def save(self, profiles):
        atomic_json(self.paths.index, {'schema': 1, 'profiles': profiles})

    def get(self, profile_id):
        self.validate_id(profile_id)
        return next(p for p in self.load() if p['id'] == profile_id)

    def create(self, name):
        name = self.validate_name(name)
        with locked(self.paths.data / 'profiles.lock'):
            profiles = self.load()
            if any(p['name'].casefold() == name.casefold() for p in profiles):
                raise ValueError('Профиль с таким названием уже существует.')
            profile = {'id': uuid.uuid4().hex, 'name': name}
            self.initialize(profile)
            self.save(profiles + [profile])
            return profile

    def rename(self, profile_id, name):
        name = self.validate_name(name)
        with locked(self.paths.data / 'profiles.lock'):
            profiles = self.load()
            if any(p['id'] != profile_id and p['name'].casefold() == name.casefold() for p in profiles):
                raise ValueError('Это название уже занято.')
            profile = next(p for p in profiles if p['id'] == profile_id)
            profile['name'] = name
            self.save(profiles)

    def delete(self, profile_id):
        with locked(self.paths.data / 'profiles.lock'):
            profiles = self.load()
            profile = next(p for p in profiles if p['id'] == profile_id)
            if running_port(self.paths, profile):
                raise RuntimeError('Сначала закрой Android этого профиля.')
            avd = self.avd(profile).resolve()
            if avd.parent != self.paths.avds.resolve():
                raise ValueError('Профиль находится за пределами каталога приложения.')
            # Rename before changing the index, so a failed filesystem operation
            # leaves the profile visible and recoverable.
            trash = avd.with_name(avd.name + '.deleted-' + uuid.uuid4().hex)
            if avd.exists():
                avd.rename(trash)
            try:
                self.save([p for p in profiles if p['id'] != profile_id])
            except Exception:
                if trash.exists():
                    trash.rename(avd)
                raise
            (self.paths.avds / (AVD_PREFIX + profile_id + '.ini')).unlink(missing_ok=True)
            if trash.exists():
                shutil.rmtree(trash)

    def avd(self, profile):
        return self.paths.avds / (AVD_PREFIX + self.validate_id(profile['id']) + '.avd')

    def initialize(self, profile):
        avd = self.avd(profile)
        avd.mkdir(parents=True, exist_ok=True)
        avd_id = AVD_PREFIX + profile['id']
        (self.paths.avds / (avd_id + '.ini')).write_text(
            f'avd.ini.encoding=UTF-8\npath={avd.resolve()}\ntarget=android-33\n', encoding='utf-8')
        config = f'''avd.ini.encoding=UTF-8
AvdId={avd_id}
avd.ini.displayname={avd_id}
abi.type=x86_64
hw.cpu.arch=x86_64
hw.cpu.ncore=2
hw.ramSize=3072
hw.lcd.width=720
hw.lcd.height=1280
hw.lcd.density=320
hw.gpu.enabled=yes
hw.gpu.mode=software
hw.keyboard=yes
hw.mainKeys=no
hw.camera.back=virtualscene
hw.camera.front=emulated
hw.device.name=pixel_2
hw.device.manufacturer=Google
hw.initialOrientation=Portrait
disk.dataPartition.size=6G
image.sysdir.1={self.paths.sdk / IMAGE}/
tag.id=google_apis_playstore
tag.display=Google Play
PlayStore.enabled=true
fastboot.forceColdBoot=no
fastboot.forceFastBoot=yes
showDeviceFrame=no
'''
        if not (avd / 'config.ini').exists():
            (avd / 'config.ini').write_text(config, encoding='utf-8')


def sdk_ready(paths):
    return all((paths.sdk / relative).is_file() for relative in (
        'emulator/emulator.exe', 'platform-tools/adb.exe', IMAGE + '/system.img', IMAGE + '/vendor.img'))


def environment(paths):
    return dict(os.environ, ANDROID_HOME=str(paths.sdk), ANDROID_SDK_ROOT=str(paths.sdk),
                ANDROID_AVD_HOME=str(paths.avds), ANDROID_USER_HOME=str(paths.data / 'android'),
                ANDROID_EMULATOR_HOME=str(paths.data / 'android'), ANDROID_ADB_SERVER_PORT=str(ADB_PORT))


def adb(paths, *args, timeout=15):
    return subprocess.run([str(paths.sdk / 'platform-tools/adb.exe'), '-P', str(ADB_PORT), *args],
                          env=environment(paths), capture_output=True, timeout=timeout,
                          creationflags=CREATE_NO_WINDOW)


def port_open(port):
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=0.2):
            return True
    except OSError:
        return False


def free_emulator_port():
    for port in range(5554, 5683, 2):
        sockets = []
        try:
            for candidate in (port, port + 1):
                sock = socket.socket()
                sockets.append(sock)
                sock.bind(('127.0.0.1', candidate))
            return port
        except OSError:
            pass
        finally:
            for sock in sockets:
                sock.close()
    raise RuntimeError('Нет свободного порта Android Emulator. Закрой один из работающих экземпляров.')


def runtime_path(paths, profile):
    return Profiles(paths).avd(profile) / 'launcher-runtime.json'


def running_port(paths, profile):
    try:
        runtime = json.loads(runtime_path(paths, profile).read_text(encoding='utf-8'))
        port = runtime['port']
        if not isinstance(port, int) or port not in range(5554, 5683, 2) or not port_open(port):
            return None
        adb(paths, 'connect', f'127.0.0.1:{port + 1}', timeout=4)
        result = adb(paths, '-s', f'127.0.0.1:{port + 1}', 'shell', 'getprop', 'ro.boot.qemu.avd_name', timeout=4)
        if result.stdout.decode(errors='replace').strip() == AVD_PREFIX + profile['id']:
            return port
        # A still-booting emulator has no ADB yet. Check its recorded process too.
        if time.time() - runtime['started'] < 240 and process_alive(runtime['pid']):
            return port
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        pass
    return None


def process_alive(pid):
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.restype = wintypes.HANDLE
    handle = kernel.OpenProcess(0x1000, False, int(pid))
    if not handle:
        return False
    code = wintypes.DWORD()
    try:
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
    finally:
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle(handle)


def start_profile(paths, profile, cold=False):
    if not sdk_ready(paths):
        raise RuntimeError('Сначала установи компоненты Android через кнопку «Установить Android».')
    profiles = Profiles(paths)
    with locked(paths.data / 'launch.lock'):
        existing = running_port(paths, profile)
        if existing:
            return existing, False
        profiles.initialize(profile)
        # Emulator cannot create its feature-lock file if this parent is missing.
        (paths.data / 'android').mkdir(parents=True, exist_ok=True)
        port = free_emulator_port()
        args = [str(paths.sdk / 'emulator/emulator.exe'), '-avd', AVD_PREFIX + profile['id'],
                '-port', str(port), '-gpu', 'software', '-feature', '-Vulkan', '-no-metrics',
                '-no-boot-anim', '-netdelay', 'none', '-netspeed', 'full']
        if cold:
            args.append('-no-snapshot-load')
        with (profiles.avd(profile) / 'emulator.log').open('ab') as log:
            proc = subprocess.Popen(args, env=environment(paths), stdout=log, stderr=log,
                                    creationflags=CREATE_NO_WINDOW)
        atomic_json(runtime_path(paths, profile), {'port': port, 'pid': proc.pid, 'started': time.time()})
        # Keep the launch lock until the emulator has claimed its port.
        for _ in range(100):
            if port_open(port):
                return port, True
            if proc.poll() is not None:
                raise RuntimeError('Эмулятор не запустился. Смотри emulator.log в папке профиля.')
            time.sleep(0.1)
        raise RuntimeError('Запуск затянулся. Подожди и повтори — данные профиля сохранены.')


def wait_ready(paths, profile, port, timeout=240):
    serial = f'127.0.0.1:{port + 1}'
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            adb(paths, 'connect', serial, timeout=5)
            result = adb(paths, '-s', serial, 'shell', 'getprop', 'sys.boot_completed', timeout=5)
            if result.stdout.strip() == b'1':
                name = adb(paths, '-s', serial, 'shell', 'getprop', 'ro.boot.qemu.avd_name', timeout=5)
                if name.stdout.decode(errors='replace').strip() != AVD_PREFIX + profile['id']:
                    raise RuntimeError('Порт занят другим устройством. Команда не отправлена.')
                return serial
        except subprocess.TimeoutExpired:
            pass
        time.sleep(2)
    raise RuntimeError('Android ещё не загрузился. Смотри журнал профиля; попробуй холодный запуск.')


def open_riot(paths, profile, port):
    serial = wait_ready(paths, profile, port)
    installed = adb(paths, '-s', serial, 'shell', 'pm', 'path', PACKAGE)
    if installed.stdout.startswith(b'package:'):
        args = ['shell', 'monkey', '-p', PACKAGE, '-c', 'android.intent.category.LAUNCHER', '1']
    else:
        args = ['shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', 'market://details?id=' + PACKAGE]
    result = adb(paths, '-s', serial, *args)
    if result.returncode or b'Error:' in result.stdout + result.stderr:
        raise RuntimeError('Открой Riot Mobile или Google Play вручную внутри Android.')


def stop_profile(paths, profile):
    port = running_port(paths, profile)
    if port is None:
        return False
    # Verify the identity again; never stop unrelated emulators.
    serial = wait_ready(paths, profile, port, timeout=15)
    del serial
    result = adb(paths, '-s', f'emulator-{port}', 'emu', 'kill', timeout=30)
    if result.returncode:
        raise RuntimeError('Не удалось закрыть профиль. Закрой окно Android крестиком.')
    return True
