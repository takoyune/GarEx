<#
.SYNOPSIS
Builds the upstream GARbro components required for the GarEx bridge (GameRes, ArcFormats, Image.Convert, Console).

.DESCRIPTION
This script uses MSBuild and the build overrides in tools/build_overrides.targets to build
the assemblies without modifying anything in vendor/GARbro.
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

# 1. Ensure nuget.exe exists
$nuget = Join-Path $PSScriptRoot "nuget.exe"
if (-not (Test-Path $nuget)) {
    Write-Host "Downloading nuget.exe..."
    Invoke-WebRequest -Uri "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe" -OutFile $nuget
}

# 2. Ensure .NET 4.6 reference assemblies exist
$refPackage = Join-Path $PSScriptRoot "packages\Microsoft.NETFramework.ReferenceAssemblies.net46.1.0.3"
if (-not (Test-Path $refPackage)) {
    Write-Host "Installing .NET 4.6 Reference Assemblies package..."
    & $nuget install Microsoft.NETFramework.ReferenceAssemblies.net46 -OutputDirectory (Join-Path $PSScriptRoot "packages")
}

# 3. Ensure vendor/GARbro exists
$garbroSln = Join-Path $root "vendor\GARbro\GARbro.sln"
if (-not (Test-Path $garbroSln)) {
    Write-Host "Cloning upstream GARbro repository into vendor\GARbro..."
    $vendorDir = Join-Path $root "vendor\GARbro"
    git clone --depth 1 https://github.com/morkt/GARbro.git $vendorDir
}

# 4. Restore NuGet packages for GARbro
Write-Host "Restoring GARbro NuGet packages..."
& $nuget restore $garbroSln

# 4. Build projects
$overrides = Join-Path $PSScriptRoot "build_overrides.targets"
$solutionDir = (Join-Path $PSScriptRoot "") + "\" # Double backslash avoids escaping the closing quote
$projects = @(
    "vendor\GARbro\GameRes\GameRes.csproj",
    "vendor\GARbro\ArcFormats\ArcFormats.csproj",
    "vendor\GARbro\Image.Convert\Image.Convert.csproj",
    "vendor\GARbro\Console\GARbro.Console.csproj"
)

foreach ($proj in $projects) {
    $fullPath = Join-Path $root $proj
    Write-Host "Building $proj..."
    & $msbuild $fullPath /p:Configuration=Release "/p:SolutionDir=$solutionDir" "/p:CustomAfterMicrosoftCommonTargets=$overrides" /v:m
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed for $proj"
    }
}

Write-Host "Successfully built all upstream GARbro components in vendor\GARbro\bin\Release\"
