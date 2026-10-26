# Building Upstream GARbro on Windows

This guide explains how to compile the upstream C# bridge components (`GameRes`, `ArcFormats`, `Image.Convert`, and `GARbro.Console`) on Windows.

> **Note**: GarEx's mainstream formats (Ren'Py RPA, KiriKiri XP3, CatSystem2 INT, NScripter SAR/NSA) run natively in pure Python without requiring these bridge assemblies. The bridge is only required if you wish to run the 800+ legacy commercial engine catalog on Windows.

---

## Prerequisites

1. **Operating System**: Windows 10 or Windows 11 (64-bit).
2. **MSBuild / Visual Studio**: Visual Studio Build Tools 2022 (or Visual Studio IDE) with MSBuild installed.
   - Default discovery tool: `vswhere.exe`.
3. **PowerShell**: Version 5.1 or PowerShell 7+.
4. **Targeting Pack for .NET Framework 4.6**:
   - The upstream C# projects target `.NETFramework,Version=v4.6`.
   - The build script automatically acquires the required targeting pack via the NuGet package `Microsoft.NETFramework.ReferenceAssemblies.net46` into `tools/packages/`.

---

## Automated One-Step Build

GarEx includes an automated build script in the `tools/` directory that handles NuGet package restoration, environment setup, and compilation:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_upstream.ps1
```

### What This Script Does

1. Locates `MSBuild.exe` via Visual Studio locator (`vswhere.exe`).
2. Downloads `tools/nuget.exe` if not already present.
3. Downloads the .NET Framework 4.6 reference assemblies package.
4. Restores all 35 NuGet packages defined in `vendor/GARbro/packages/repositories.config`.
5. Builds the following assemblies in `Release` configuration into `vendor/GARbro/bin/Release/`:
   - `GameRes.dll` (Core format definitions and archive engine)
   - `ArcFormats.dll` (Comprehensive visual novel archive catalog)
   - `Image.Convert.exe` (Image format conversion CLI)
   - `GARbro.Console.exe` (Archive extraction and repacking CLI)

---

## Build Architecture & Non-Intrusive Overrides

All build adjustments are managed externally via MSBuild properties and `tools/build_overrides.targets` so that the upstream `vendor/GARbro` submodule remains completely clean and untouched:

1. **Modern Windows SDK Compatibility**:
   - Upstream projects target .NET 4.6, which is omitted by default in newer Windows 10/11 SDKs.
   - Reference assemblies are supplied via NuGet and passed to MSBuild through the `TargetFrameworkRootPath` property.
2. **Satellite Assembly Linking Workaround**:
   - When building without Visual Studio's optional localized language tools, satellite assembly compilation (`al.exe`) is bypassed in `tools/build_overrides.targets`, embedding default common strings cleanly.
3. **Pre-build Script Compatibility**:
   - The build script handles revision string generation without requiring external Perl dependencies.

---

## Output Artifacts

Upon successful compilation, binaries are located in `vendor/GARbro/bin/Release/`:
- `GameRes.dll`
- `ArcFormats.dll`
- `Image.Convert.exe`
- `GARbro.Console.exe`
- `GameData/Formats.dat` (Upstream format catalog database)
- Runtime dependencies: `NAudio.dll`, `NVorbis.dll`, `ICSharpCode.SharpZipLib.dll`, `Net20.dll`, `System.Memory.dll`.
