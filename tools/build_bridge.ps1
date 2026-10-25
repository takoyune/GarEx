<#
.SYNOPSIS
Builds the GarexBridge project.
#>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$vswhere = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"

if (-not (Test-Path $vswhere)) {
    throw "vswhere.exe not found at $vswhere"
}

$msbuild = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -find MSBuild\**\Bin\MSBuild.exe | Select-Object -First 1
if (-not $msbuild -or -not (Test-Path $msbuild)) {
    throw "MSBuild.exe not found."
}

Write-Host "Using MSBuild: $msbuild"
$overrides = Join-Path $PSScriptRoot "build_overrides.targets"
$proj = Join-Path $root "bridge\GarexBridge.csproj"

& $msbuild $proj /p:Configuration=Release "/p:CustomAfterMicrosoftCommonTargets=$overrides" /v:m
if ($LASTEXITCODE -ne 0) {
    throw "Build failed for GarexBridge"
}

Write-Host "Successfully built GarexBridge in bridge\bin\Release\"
