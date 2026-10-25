<!--
FILE CONTRACT
Purpose : Map of the upstream GARbro repository: what each folder is and whether it matters for garex.
Status  : DRAFT. "Initial reading" column comes from the repo's public page and is NOT verified. Agent fills "VERIFIED" in Phase 0 task 0.5 after reading the code, then removes uncertainty notes.
-->

# GARbro repository map

Upstream: https://github.com/morkt/GARbro (C#, .NET Framework 4.6+, MIT). Solution file: `GARbro.sln`.

| Folder / file | Initial reading (unverified) | Relevance to garex | VERIFIED (agent fills) |
|---|---|---|---|
| `GameRes/` | Core library: base abstractions for archives, images, audio, format catalog | HIGH - the heart of the bridge and the model for the Python API | VERIFIED: Core abstractions (`ArchiveFormat`, `ImageFormat`, `AudioFormat`, `ScriptFormat`, `ArcFile`, `FormatCatalog`, `VFS`). Uses MEF for discovery. References `PresentationCore` for `BitmapSource`. |
| `ArcFormats/` | Large set of archive/format implementations for many game engines | HIGH - main source of formats to port | VERIFIED: 100+ game engine implementations exported via MEF attributes (`[Export(typeof(ArchiveFormat))]`). |
| `Image.Convert/` | Image conversion helpers | HIGH for Phase 3 | VERIFIED: Standalone CLI tool converting proprietary game images into PNG/BMP/etc. using `GameRes.ImageFormat`. |
| `Legacy/` | Older/legacy engine formats | MEDIUM - port late | VERIFIED: Contains older/legacy formats (DOS/Win9x engines), depends on `GameRes`. |
| `Experimental/` | Experimental formats | LOW - port last, maybe never | VERIFIED: In-development / incomplete reverse engineered formats. |
| `Console/` | Command-line front end | MEDIUM - reference for how upstream drives the library | VERIFIED: CLI client supporting `-l` (list formats), `-x` (extract all), single entry extraction, and `-c` (convert images). |
| `GUI/` | WPF desktop interface | NONE - ignore | VERIFIED: Full WPF desktop UI with archive browser, hex viewer, image preview. Ignored for garex. |
| `Net20/` | Likely a .NET 2.0-targeted variant | LOW - check why it exists | VERIFIED: Compatibility helper library (`Net20.dll`) providing backports for .NET Framework 2.0 runtime methods. |
| `docs/` | Upstream docs / supported formats page | MEDIUM - source for format list | VERIFIED: Contains HTML/MD lists of supported visual novel titles and formats. |
| `packages/` | NuGet packages | LOW - needed to build only | VERIFIED: NuGet package dependencies restored via `tools/nuget.exe`. |
| `GARbro.sln` | Solution file | needed to build | VERIFIED: Visual Studio solution targeting .NET 4.6. |
| `GARbro.nsi` | Installer script | NONE | VERIFIED: Nullsoft installer script for Windows distribution. |
| `inc-revision.pl` | Version bump script | NONE | VERIFIED: Pre-build revision incrementer (non-fatal `exit 0` fallback). |
| `LICENSE` | MIT license text | MUST copy into wheel | VERIFIED: MIT license, copied to `licenses/LICENSE-GARbro.txt`. |

## Questions answered from upstream source:
1. **Which classes are the extension points for archives, images, audio, scripts?**
   - Base classes derived from `GameRes.IResource`:
     - Archive: `GameRes.ArchiveFormat` (`[Export(typeof(ArchiveFormat))]`) implementing `TryOpen`, `Open`, `Create`.
     - Image: `GameRes.ImageFormat` (`[Export(typeof(ImageFormat))]`) implementing `Read`, `Write`.
     - Audio: `GameRes.AudioFormat` (`[Export(typeof(AudioFormat))]`) implementing `Read`, `Write`.
     - Script: `GameRes.ScriptFormat` (`[Export(typeof(ScriptFormat))]`) implementing `Read`, `Write`.
2. **How are format implementations discovered at runtime?**
   - Managed Extensibility Framework (MEF, `System.ComponentModel.Composition`): `FormatCatalog` creates an `AggregateCatalog` scanning `GameRes.dll` and `Arc*.dll` (like `ArcFormats.dll`).
3. **Where are game schemes/keys stored and in what serialization?**
   - In `GameData/Formats.dat`.
   - Serialized as a zlib-compressed .NET `BinaryFormatter` stream of `GameRes.SchemeDataBase`, containing `SchemeMap` (tags -> `ResourceScheme`) and `GameMap` (filenames -> game titles).
4. **Which projects depend on WPF/System.Windows types?**
   - `GameRes` (`ImageData` wraps `System.Windows.Media.Imaging.BitmapSource` from `PresentationCore`), `ArcFormats`, `Legacy`, and `GUI`.
5. **What does `Console/` support (list/extract/create/convert) and with which options?**
   - `-l`: List recognized archive formats.
   - `-x`: Extract all entries in archive.
   - `[ENTRIES]`: Extract specific entries.
   - `-c <FORMAT>`: Convert images to format tag (e.g. `PNG`).
   - Default: List entries with size and offset. Does not support archive creation.
