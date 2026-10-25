"""Command line interface for garex."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import garex


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="garex",
        description="Visual novel archive browser, extractor, and converter (GARbro port).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {garex.__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list subcommand
    list_parser = subparsers.add_parser("list", help="List files inside an archive.")
    list_parser.add_argument("archive", type=str, help="Path to archive file.")
    list_parser.add_argument(
        "--backend",
        choices=["auto", "bridge", "native"],
        default="auto",
        help="Backend to use (default: auto).",
    )

    # formats subcommand
    formats_parser = subparsers.add_parser("formats", help="List all supported resource formats.")
    formats_parser.add_argument(
        "--kind",
        choices=["all", "archive", "image", "audio", "script"],
        default="all",
        help="Filter formats by kind (default: all).",
    )

    # extract subcommand
    extract_parser = subparsers.add_parser("extract", help="Extract files from an archive.")
    extract_parser.add_argument("archive", type=str, help="Path to archive file.")
    extract_parser.add_argument(
        "-o", "--output",
        type=str,
        default=".",
        help="Destination directory for extracted files (default: current directory).",
    )
    extract_parser.add_argument(
        "--entry",
        type=str,
        default=None,
        help="Extract only the specified single entry instead of all entries.",
    )
    extract_parser.add_argument(
        "--backend",
        choices=["auto", "bridge", "native"],
        default="auto",
        help="Backend to use (default: auto).",
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "list":
            return cmd_list(args.archive, backend=args.backend)
        if args.command == "formats":
            return cmd_formats(kind=args.kind)
        if args.command == "extract":
            return cmd_extract(args.archive, output=args.output, entry=args.entry, backend=args.backend)
    except garex.GarexError as ex:
        sys.stderr.write(f"Error: {ex}\n")
        return 1
    except Exception as ex:
        sys.stderr.write(f"Unexpected error: {ex}\n")
        return 2

    return 0


def cmd_extract(
    archive_path: str,
    output: str = ".",
    entry: str | None = None,
    backend: str = "auto",
) -> int:
    path = Path(archive_path)
    dest = Path(output)
    with garex.open_archive(path, backend=backend) as arc:  # type: ignore[arg-type]
        if entry:
            print(f"Extracting '{entry}' from {arc.path.name} to {dest}...")
            target = arc.extract(entry, destination=dest)
            print(f"Extracted: {target}")
        else:
            print(f"Extracting {len(arc)} entries from {arc.path.name} to {dest}...")

            def progress(current: int, total: int, e: garex.models.Entry) -> None:
                print(f"  [{current}/{total}] {e.name} ({e.size} bytes)")

            arc.extract_all(destination=dest, progress_callback=progress)
            print("Extraction complete.")

    return 0


def cmd_list(archive_path: str, backend: str = "auto") -> int:
    path = Path(archive_path)
    with garex.open_archive(path, backend=backend) as arc:  # type: ignore[arg-type]
        print(f"Archive: {arc.path.name}")
        print(f"Format:  {arc.format} ({arc.description})")
        print(f"Entries: {len(arc)}\n")
        print(f"{'Size (bytes)':>12}  {'Packed':>10}  {'Offset':>10}  Name")
        print("-" * 65)

        for entry in arc.entries():
            packed_str = f"{entry.packed_size}" if entry.packed_size is not None else "-"
            offset_str = f"0x{entry.offset:08X}" if entry.offset >= 0 else "-"
            print(f"{entry.size:>12}  {packed_str:>10}  {offset_str:>10}  {entry.name}")

    return 0


def cmd_formats(kind: str = "all") -> int:
    formats = garex.supported_formats()
    if kind != "all":
        formats = [f for f in formats if f.kind == kind]

    print(f"{'Tag':<12} {'Kind':<8} {'Status':<8} {'Exts':<18} Description")
    print("-" * 75)
    for f in formats:
        exts = ", ".join(f.extensions[:3]) if f.extensions else "-"
        print(f"{f.tag:<12} {f.kind:<8} {f.status:<8} {exts:<18} {f.description}")

    print(f"\nTotal: {len(formats)} formats")
    return 0


if __name__ == "__main__":
    sys.exit(main())
