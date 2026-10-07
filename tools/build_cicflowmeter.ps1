$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$sourceRoot = Join-Path $PSScriptRoot "CICFlowMeter-src-20260820\CICFlowMeter-master"
$jdk = Get-ChildItem "C:\Program Files\Eclipse Adoptium" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "jdk-8*" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $jdk) {
    throw "Temurin JDK 8 was not found. Install EclipseAdoptium.Temurin.8.JDK with winget first."
}

$env:JAVA_HOME = $jdk.FullName
$env:Path = "$($jdk.FullName)\bin;$env:Path"

Push-Location $sourceRoot
try {
    & .\gradlew.bat clean installDist --no-daemon
    if ($LASTEXITCODE -ne 0) {
        throw "CICFlowMeter Gradle build failed with exit code $LASTEXITCODE."
    }
} finally {
    Pop-Location
}

$launcher = Join-Path $sourceRoot "build\install\CICFlowMeter\bin\cfm.bat"
if (-not (Test-Path -LiteralPath $launcher)) {
    throw "Build finished without creating $launcher"
}

Write-Host "CICFlowMeter ready: $launcher"
