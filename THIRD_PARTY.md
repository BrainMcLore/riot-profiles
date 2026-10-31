# Third-party components and branding

The MIT license applies to the launcher source and the project-created phone icon.
It does not relicense Android, Google Play, Riot Mobile or any third-party package.

- Android Emulator, platform-tools and the Google Play Android 13 x86_64 image are
  downloaded directly from `https://dl.google.com/android/repository/` at install time.
  Their license text is loaded from Google's SDK catalogs and displayed before the
  user accepts it. It is saved locally after installation. No SDK or system image is
  included in source archives or release executables.
- Google SDK terms: https://developer.android.com/studio/terms
- Google Play system-image catalog and licenses:
  https://dl.google.com/android/repository/sys-img/google_apis_playstore/sys-img2-1.xml
- Python: https://docs.python.org/3/license.html
- PyInstaller: https://pyinstaller.org/en/stable/license.html
  The build uses its distribution exception; the executable contains the Python
  runtime and PyInstaller bootloader under their respective licenses.

The red/black desktop design is independently implemented. This is an unofficial
community project, not affiliated with, endorsed by, or supported by Riot Games or
Google. Riot Games, Riot Mobile, Android and Google Play are their owners' trademarks.
Riot Mobile must be installed separately from Google Play. Its account, MFA, QR and
device compatibility requirements are controlled by Riot; operation in an emulator
is not guaranteed. The project does not bypass them.

Release binaries are unsigned unless the maintainer signs them. SHA256SUMS detects
corruption; a checksum hosted with a release does not prove the publisher's identity.
