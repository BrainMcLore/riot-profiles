import argparse
import ctypes
import json
import os
import platform
import sys

from app import core, install, windows, i18n


def main():
    parser = argparse.ArgumentParser(description='Independent Android profiles for Riot Mobile')
    parser.add_argument('--profile', help='Start a profile ID directly, without the launcher UI')
    parser.add_argument('--cold', action='store_true')
    parser.add_argument('--setup', action='store_true')
    parser.add_argument('--headless-install', action='store_true')
    parser.add_argument('--accept-google-licenses', action='store_true')
    parser.add_argument('--smoke-test', action='store_true', help='Validate bundled resources without modifying user data')
    args = parser.parse_args()
    if args.smoke_test:
        if not (windows.payload() / 'phone.ico').is_file():
            raise RuntimeError('Missing icon')
        if not (windows.payload() / 'LICENSE.txt').is_file():
            raise RuntimeError('Missing license')
        return
    if os.name != 'nt':
        raise RuntimeError('Riot Profiles supports Windows only.')
    if platform.machine().lower() not in ('amd64', 'x86_64'):
        raise RuntimeError('Требуется Windows x64 на процессоре Intel или AMD.')
    paths = core.Paths.default()
    if args.headless_install:
        if not args.accept_google_licenses:
            raise RuntimeError('Use --accept-google-licenses only after reading https://developer.android.com/studio/terms and the Google Play image license in the SDK catalog.')
        install.install_sdk(paths, install.plan_install(), True)
        windows.install_app()
        return
    if args.profile:
        profile = core.Profiles(paths).get(args.profile)
        core.start_profile(paths, profile, args.cold)
        windows.focus_profile(profile['id'])
        return
    # A setup binary is the same auditable program, not a separate closed installer.
    setup = args.setup or 'setup' in os.path.basename(sys.executable).lower()
    if setup:
        windows.install_app()
    from app.ui import Launcher
    prompt_language = True
    selected_profile = None
    while True:
        app = Launcher(paths, setup=setup, prompt_language=prompt_language, selected_profile=selected_profile)
        if app.cancelled:
            return
        app.mainloop()
        if not app.restart:
            break
        prompt_language = False
        selected_profile = app.last_selected
        setup = False


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        try:
            translator = i18n.Translator(i18n.preferences(core.Paths.default()).get('language', 'en'))
            text = translator.message(str(error))
        except Exception:
            text = str(error)
        if getattr(sys, 'frozen', False) and '--smoke-test' not in sys.argv and '--headless-install' not in sys.argv:
            ctypes.windll.user32.MessageBoxW(None, text, 'Riot Profiles', 16)
        else:
            print(text, file=sys.stderr)
        sys.exit(1)
