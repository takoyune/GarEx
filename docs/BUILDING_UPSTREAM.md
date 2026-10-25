# Building Upstream GARbro on Windows

This document details the build prerequisites, instructions, and build-time workarounds for compiling upstream GARbro components (`GameRes`, `ArcFormats`, `Image.Convert`, `Console`) on Windows without modifying any files in `vendor/GARbro`.

## Prerequisites

1. **Operating System**: Windows 10 or Windows 11 (64-bit).
2. **MSBuild / Visual Studio**: Visual Studio Build Tools 2022/2026 or Visual Studio IDE with the MSBuild component.
   - Default discovery path: `C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe`.
3. **PowerShell**: Version 5.1 or PowerShell 7+.
4. **Targeting Pack for .NET Framework 4.6**:
   - The projects target `.NETFramework,Version=v4.6`.
   - Instead of requiring an obsolete system-wide Windows SDK Developer Pack, the required reference assemblies are provided via the NuGet package `Microsoft.NETFramework.ReferenceAssemblies.net46` installed to `tools/packages/`.
5. **NuGet Command Line**: `tools/nuget.exe` (automatically acquired if not present).

## Automated Build Script

To build all required upstream components in a single command, run:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_upstream.ps1
```

This script performs the following steps:
1. Locates `MSBuild.exe` via `vswhere.exe`.
2. Downloads `tools/nuget.exe` if not present.
3. Installs `Microsoft.NETFramework.ReferenceAssemblies.net46` to supply the .NET Framework 4.6 targeting pack.
4. Restores all 35 NuGet packages defined in `vendor/GARbro/packages/repositories.config`.
5. Builds the following projects in `Release` configuration into `vendor/GARbro/bin/Release/`:
   - `GameRes.csproj` -> `GameRes.dll`
   - `ArcFormats.csproj` -> `ArcFormats.dll` (and dependency `Net20.dll`)
   - `Image.Convert.csproj` -> `Image.Convert.exe`
   - `GARbro.Console.csproj` -> `GARbro.Console.exe`

## Build Challenges & Non-Intrusive Overrides

In accordance with `docs/05_DO_AND_DONT.md` ("Never edit files in vendor/"), all build adjustments are handled externally via MSBuild properties and `tools/build_overrides.targets`:

1. **Missing .NET Framework 4.6 Targeting Pack (`MSB3644`)**:
   - *Issue*: Modern Windows SDKs often lack old .NET 4.6 Developer Packs.
   - *Fix*: The reference assemblies are downloaded as a NuGet package (`Microsoft.NETFramework.ReferenceAssemblies.net46`) and passed via `/p:TargetFrameworkRootPath=...` in `tools/build_overrides.targets`.
2. **Obsolete `.nuget/NuGet.targets` Check**:
   - *Issue*: `GameRes.csproj` and `ArcFormats.csproj` contain a legacy check (`EnsureNuGetPackageBuildImports`) that asserts `$(SolutionDir)\.nuget\NuGet.targets` exists. Upstream's `.nuget` folder is gitignored and not committed.
   - *Fix*: `tools/.nuget/NuGet.targets` is created, and `/p:SolutionDir=".../tools\\"` is supplied along with an override target in `tools/build_overrides.targets` to bypass the error check.
3. **Missing `al.exe` for Satellite Assemblies (`MSB3086`)**:
   - *Issue*: The projects have localized `.resx` resources (e.g. Russian, Japanese, Chinese). When the Windows SDK .NET FX tools (`al.exe` Assembly Linker) are not installed system-wide, satellite assembly linking fails.
   - *Fix*: In `tools/build_overrides.targets`, `GenerateSatelliteAssemblies` is overridden to clear `IntermediateSatelliteAssembliesWithTargetPath`. The core assemblies build and embed the default common strings without satellite resource DLLs.
4. **Optional Perl Script (`inc-revision.pl`)**:
   - *Issue*: PreBuildEvent tries to run `perl inc-revision.pl`.
   - *Fix*: The project pre-build command specifies `exit 0`, so having or not having Perl does not break compilation.

## Output Artifacts

Compiled binaries are placed in `vendor/GARbro/bin/Release/`:
- `GameRes.dll`
- `ArcFormats.dll`
- `Image.Convert.exe`
- `GARbro.Console.exe`
- `GameData/Formats.dat` (Format catalog database)
- Runtime dependencies: `NAudio.dll`, `NVorbis.dll`, `ICSharpCode.SharpZipLib.dll`, `Net20.dll`, `System.Memory.dll`.
