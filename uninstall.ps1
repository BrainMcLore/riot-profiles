[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$program = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs/RiotProfiles'))
Write-Host 'This removes the launcher only. All Android profiles, SDK and accounts will be preserved.'
if ((Read-Host 'Type UNINSTALL to continue') -cne 'UNINSTALL') { return }
$exe = Join-Path $program 'RiotProfiles.exe'
if (Get-Process -Name RiotProfiles -ErrorAction SilentlyContinue) { throw 'Close Riot Profiles first.' }
foreach ($name in @('RiotProfiles.exe','phone.ico','LICENSE.txt','THIRD_PARTY_LICENSES.txt')) {
    $target=[IO.Path]::GetFullPath((Join-Path $program $name))
    if ([IO.Path]::GetDirectoryName($target) -ne $program) { throw 'Unexpected uninstall path' }
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target }
}
$shell=New-Object -ComObject WScript.Shell
Get-ChildItem -LiteralPath ([Environment]::GetFolderPath('Desktop')) -Filter '*.lnk' | ForEach-Object {
    if ($shell.CreateShortcut($_.FullName).TargetPath -eq $exe) { Remove-Item -LiteralPath $_.FullName }
}
Write-Host 'Launcher removed. Profile data was preserved.'
