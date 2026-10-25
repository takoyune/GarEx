<!--
FILE CONTRACT
Purpose : Map of the upstream GARbro repository: what each folder is and whether it matters for garex.
Status  : DRAFT. "Initial reading" column comes from the repo's public page and is NOT verified. Agent fills "VERIFIED" in Phase 0 task 0.5 after reading the code, then removes uncertainty notes.
-->

# GARbro repository map

Upstream: https://github.com/morkt/GARbro (C#, .NET Framework 4.6+, MIT). Solution file: `GARbro.sln`.

| Folder / file | Initial reading (unverified) | Relevance to garex | VERIFIED (agent fills) |
|---|---|---|---|
| `GameRes/` | Core library: base abstractions for archives, images, audio, format catalog | HIGH - the heart of the bridge and the model for the Python API | |
| `ArcFormats/` | Large set of archive/format implementations for many game engines | HIGH - main source of formats to port | |
| `Image.Convert/` | Image conversion helpers | HIGH for Phase 3 | |
| `Legacy/` | Older/legacy engine formats | MEDIUM - port late | |
| `Experimental/` | Experimental formats | LOW - port last, maybe never | |
| `Console/` | Command-line front end | MEDIUM - reference for how upstream drives the library | |
| `GUI/` | WPF desktop interface | NONE - ignore | |
| `Net20/` | Likely a .NET 2.0-targeted variant | LOW - check why it exists | |
| `docs/` | Upstream docs / supported formats page | MEDIUM - source for format list | |
| `packages/` | NuGet packages | LOW - needed to build only | |
| `GARbro.sln` | Solution file | needed to build | |
| `GARbro.nsi` | Installer script | NONE | |
| `inc-revision.pl` | Version bump script | NONE | |
| `LICENSE` | MIT license text | MUST copy into wheel | |

## Questions the agent must answer while verifying
1. Which classes are the extension points for archives, images, audio, scripts?
2. How are format implementations discovered at runtime?
3. Where are game schemes/keys stored and in what serialization?
4. Which projects depend on WPF/System.Windows types?
5. What does `Console/` support (list/extract/create/convert) and with which options?
