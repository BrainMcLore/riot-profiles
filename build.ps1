[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    python tools/bundle_notices.py
    if ($LASTEXITCODE -ne 0) { throw 'Runtime license collection failed' }
    python -m PyInstaller --clean --noconfirm --onefile --windowed --name RiotProfiles --icon assets/phone.ico --add-data 'assets:assets' main.py
    if ($LASTEXITCODE -ne 0) { throw 'EXE build failed' }
    $release = Join-Path $PSScriptRoot 'release'
    New-Item -ItemType Directory -Path $release -Force | Out-Null
    Copy-Item -LiteralPath 'dist/RiotProfiles.exe' -Destination (Join-Path $release 'RiotProfiles.exe') -Force
    Copy-Item -LiteralPath 'dist/RiotProfiles.exe' -Destination (Join-Path $release 'RiotProfiles-Setup.exe') -Force
    Copy-Item -LiteralPath 'install.ps1' -Destination $release -Force
    $smoke = Start-Process -FilePath (Join-Path $release 'RiotProfiles.exe') -ArgumentList '--smoke-test' -WindowStyle Hidden -PassThru -Wait
    if ($smoke.ExitCode -ne 0) { throw 'Bundled EXE smoke test failed' }
    python tools/package_source.py
    if ($LASTEXITCODE -ne 0) { throw 'Source package failed' }
    python tools/audit_release.py
    if ($LASTEXITCODE -ne 0) { throw 'Release privacy audit failed' }
    $sums = Get-ChildItem -LiteralPath $release -File | Where-Object { $_.Name -ne 'SHA256SUMS' } | Sort-Object Name | ForEach-Object {
        $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        "$hash  $($_.Name)"
    }
    [IO.File]::WriteAllLines((Join-Path $release 'SHA256SUMS'), [string[]]$sums, [Text.Encoding]::ASCII)
    Write-Host "Release files: $release"
} finally {
    Pop-Location
}
