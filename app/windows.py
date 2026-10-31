"""Per-user shortcuts and installation; no administrator rights required."""
import ctypes
import os
from pathlib import Path
import shutil
import subprocess
import sys

from .core import CREATE_NO_WINDOW


def payload():
    return Path(__file__).resolve().parent.parent / 'assets'


def install_app():
    if not getattr(sys, 'frozen', False):
        return None
    folder = (Path(os.environ['LOCALAPPDATA']) / 'Programs/RiotProfiles').resolve()
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / 'RiotProfiles.exe'
    source = Path(sys.executable).resolve()
    if source != target:
        temporary = folder / 'RiotProfiles.new.exe'
        shutil.copy2(source, temporary)
        try:
            temporary.replace(target)
        except PermissionError as error:
            temporary.unlink(missing_ok=True)
            raise RuntimeError('Закрой все окна Riot Profiles и повтори обновление. Данные профилей сохранены.') from error
    for name in ('phone.ico', 'LICENSE.txt', 'THIRD_PARTY_LICENSES.txt'):
        shutil.copy2(payload() / name, folder / name)
    create_shortcut(target)
    return target


def create_shortcut(executable=None, profile=None):
    if executable is None:
        if not getattr(sys, 'frozen', False):
            raise RuntimeError('Создание ярлыков доступно в EXE-версии.')
        executable = Path(sys.executable).resolve()
    executable = Path(executable).resolve()
    # Use an ID for the filename: user-provided names never become file paths.
    label = 'Riot Profiles' if profile is None else 'Riot Profile ' + profile['id'][:12]
    arguments = '' if profile is None else '--profile ' + profile['id']
    environment = dict(os.environ, RP_TARGET=str(executable), RP_LABEL=label,
                       RP_ARGUMENTS=arguments, RP_ICON=str(executable.parent / 'phone.ico'))
    script = '''$ErrorActionPreference='Stop'
$shell=New-Object -ComObject WScript.Shell
$desktop=[Environment]::GetFolderPath('Desktop')
$link=$shell.CreateShortcut((Join-Path $desktop ($env:RP_LABEL+'.lnk')))
$link.TargetPath=$env:RP_TARGET
$link.Arguments=$env:RP_ARGUMENTS
$link.WorkingDirectory=Split-Path -LiteralPath $env:RP_TARGET
$link.IconLocation=$env:RP_ICON+',0'
$link.Save()
'''
    result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                            env=environment, capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=30)
    if result.returncode:
        raise RuntimeError('Не удалось создать ярлык на рабочем столе.')


def focus_profile(profile_id):
    from ctypes import wintypes
    user = ctypes.WinDLL('user32')
    user.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user.SetForegroundWindow.argtypes = [wintypes.HWND]
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def visit(window, _):
        text = ctypes.create_unicode_buffer(512)
        user.GetWindowTextW(window, text, len(text))
        if 'rp_' + profile_id in text.value:
            user.ShowWindow(window, 9)
            user.SetForegroundWindow(window)
            return False
        return True
    callback = callback_type(visit)
    user.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user.EnumWindows(callback, 0)
