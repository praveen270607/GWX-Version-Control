param(
    [string]$Version = "0.1.1"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$buildEnvironment = Join-Path $projectRoot ".build-env"
$distDirectory = Join-Path $projectRoot "dist"
$workDirectory = Join-Path $projectRoot "build"
$releaseDirectory = Join-Path $workDirectory "release"
$releaseVersion = $Version.TrimStart("v")

Push-Location $projectRoot
try {
    if (-not (Test-Path $buildEnvironment)) {
        python -m venv $buildEnvironment
    }

    $python = Join-Path $buildEnvironment "Scripts\python.exe"
    & $python -m pip install --upgrade pip
    & $python -m pip install ".[build]"

    Remove-Item -Recurse -Force $workDirectory -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force $distDirectory -ErrorAction SilentlyContinue

    & $python -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --name gwx `
        --collect-submodules matcher `
        main.py

    New-Item -ItemType Directory -Path $releaseDirectory -Force | Out-Null
    Copy-Item "$distDirectory\gwx.exe" "$releaseDirectory\gwx.exe"
    Copy-Item "README.md" "$releaseDirectory\README.md"
    Copy-Item "INSTALL-WINDOWS.txt" "$releaseDirectory\INSTALL-WINDOWS.txt"

    $archive = "$distDirectory\GWX-Version-Control-v$releaseVersion-windows.zip"
    Compress-Archive -Path "$releaseDirectory\*" -DestinationPath $archive -Force

    Write-Host "Created $archive"
}
finally {
    Pop-Location
}
