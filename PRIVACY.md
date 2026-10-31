# Privacy

Riot Profiles does not request Riot or Google credentials and does not send analytics.
Login happens inside the official Android apps, which have their own privacy policies.
An Android profile is a separate AVD with its own userdata, encryption key, snapshots,
installed applications and account storage. The base system image is shared read-only.
Profiles are **not** a security boundary against other Windows users with filesystem
access, local administrators or malware. Host ADB credentials are shared by the launcher.

Runtime files are stored only on the user's PC:

- `%LOCALAPPDATA%\RiotProfiles\data\profiles.json`: profile IDs and display names.
- `%LOCALAPPDATA%\RiotProfiles\data\settings.json`: interface language and startup-picker preference only.
- `%LOCALAPPDATA%\RiotProfiles\data\avd`: Android device data and per-profile logs.
- `%LOCALAPPDATA%\RiotProfiles\sdk`: shared Android tools and read-only system image.
- `%LOCALAPPDATA%\RiotProfiles\downloads`: cached official installation archives.
- `%LOCALAPPDATA%\Programs\RiotProfiles`: installed launcher and icon.

The launcher uses its own ADB server on localhost port 5041. It does not stop another
ADB server, import an existing device, scan credentials, or modify other emulators.
It only stops a device after checking that its AVD ID matches the selected profile.

Do not publish runtime folders, Android snapshots, logs, ADB keys or screen captures
of account pages. The source packager uses an explicit allowlist and does not read
those locations. The repository ignores runtime files as a second precaution.

Deleting a profile requires confirmation and destroys that profile's local data.
Uninstalling the launcher with `uninstall.ps1` preserves all Android data.
