# Download this script, inspect it, then run it. No Invoke-Expression required.
[CmdletBinding(DefaultParameterSetName='GitHub')]
param(
    [Parameter(ParameterSetName='GitHub')]
    [ValidatePattern('^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')]
    [string]$Repository = 'BrainMcLore/riot-profiles',
    [Parameter(ParameterSetName='GitHub')]
    [ValidatePattern('^[A-Za-z0-9_.-]+$')]
    [string]$Version = 'latest',
    [Parameter(Mandatory, ParameterSetName='Local')]
    [string]$SetupPath,
    [Parameter(ParameterSetName='Local')]
    [string]$ChecksumFile,
    [switch]$AcceptGoogleLicenses
)
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
if (-not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {
    throw 'Windows x64 on an Intel/AMD processor is required.'
}
if ($PSCmdlet.ParameterSetName -eq 'GitHub') {
    $cache = Join-Path $env:LOCALAPPDATA ('RiotProfiles/installer-cache/' + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $cache -Force | Out-Null
    $base = if ($Version -eq 'latest') { "https://github.com/$Repository/releases/latest/download" } else { "https://github.com/$Repository/releases/download/$Version" }
    $SetupPath = Join-Path $cache 'RiotProfiles-Setup.exe'
    $ChecksumFile = Join-Path $cache 'SHA256SUMS'
    Invoke-WebRequest -UseBasicParsing -Uri "$base/SHA256SUMS" -OutFile $ChecksumFile
    Invoke-WebRequest -UseBasicParsing -Uri "$base/RiotProfiles-Setup.exe" -OutFile $SetupPath
} else {
    $SetupPath = (Resolve-Path -LiteralPath $SetupPath).Path
    if (-not $ChecksumFile) { $ChecksumFile = Join-Path (Split-Path -LiteralPath $SetupPath) 'SHA256SUMS' }
}
$leaf = Split-Path -Leaf $SetupPath
$matchesFound = @(Get-Content -LiteralPath $ChecksumFile | Where-Object { $_ -match ('^[a-fA-F0-9]{64}\s+\*?' + [regex]::Escape($leaf) + '$') })
if ($matchesFound.Count -ne 1) { throw 'Expected exactly one checksum entry for the installer.' }
$expected = ($matchesFound[0] -split '\s+')[0]
$actual = (Get-FileHash -LiteralPath $SetupPath -Algorithm SHA256).Hash
if ($actual -ne $expected) { throw 'Installer checksum mismatch. Nothing was launched.' }
$arguments = @('--setup')
if ($AcceptGoogleLicenses) {
    Write-Host 'You explicitly accepted the Google SDK and Google Play system-image licenses. See README and THIRD_PARTY.md.'
    $arguments = @('--headless-install', '--accept-google-licenses')
}
$process = Start-Process -FilePath $SetupPath -ArgumentList $arguments -PassThru -Wait
if ($process.ExitCode -ne 0) { throw "Installer exited with code $($process.ExitCode)." }
Write-Host 'Finished. Use the Riot Profiles desktop shortcut. Android data stays separate from other emulators.'
