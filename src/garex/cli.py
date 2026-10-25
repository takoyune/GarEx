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
        "--convert",
        action="store_true",
        help="Automatically convert extracted images and audio to standard formats.",
    )
    extract_parser.add_argument(
        "--image-format",
        type=str,
        default="png",
        help="Target format for image conversion (default: png).",
    )
    extract_parser.add_argument(
        "--audio-format",
        type=str,
        default="wav",
        help="Target format for audio conversion (default: wav).",
    )
    extract_parser.add_argument(
        "--backend",
        choices=["auto", "bridge", "native"],
        default="auto",
        help="Backend to use (default: auto).",
    )

    # convert subcommand
    convert_parser = subparsers.add_parser("convert", help="Convert visual novel image or audio file.")
    convert_parser.add_argument("source", type=str, help="Path to source image or audio file.")
    convert_parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Path for converted output file.",
    )
    convert_parser.add_argument(
        "--format",
        type=str,
        default=None,
        help="Target format (default: deduced from output extension or 'png'/'wav').",
    )
    convert_parser.add_argument(
        "--type",
        choices=["auto", "image", "audio"],
        default="auto",
        help="Resource type (default: auto).",
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "list":
            return cmd_list(args.archive, backend=args.backend)
        if args.command == "formats":
            return cmd_formats(kind=args.kind)
        if args.command == "extract":
            return cmd_extract(
                args.archive,
                output=args.output,
                entry=args.entry,
                convert=args.convert,
                image_format=args.image_format,
                audio_format=args.audio_format,
                backend=args.backend,
            )
        if args.command == "convert":
            return cmd_convert(args.source, args.output, fmt=args.format, res_type=args.type)
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
    convert: bool = False,
    image_format: str = "png",
    audio_format: str = "wav",
    backend: str = "auto",
) -> int:
    path = Path(archive_path)
    dest = Path(output)
    with garex.open_archive(path, backend=backend) as arc:  # type: ignore[arg-type]
        if entry:
            print(f"Extracting '{entry}' from {arc.path.name} to {dest} (convert={convert})...")
            target = arc.extract(
                entry,
                destination=dest,
                convert=convert,
                image_format=image_format,
                audio_format=audio_format,
            )
            print(f"Extracted: {target}")
        else:
            print(f"Extracting {len(arc)} entries from {arc.path.name} to {dest} (convert={convert})...")

            def progress(current: int, total: int, e: garex.models.Entry) -> None:
                print(f"  [{current}/{total}] {e.name} ({e.size} bytes)")

            arc.extract_all(
                destination=dest,
                convert=convert,
                image_format=image_format,
                audio_format=audio_format,
                progress_callback=progress,
            )
            print("Extraction complete.")

    return 0


def cmd_convert(
    source_path: str,
    output_path: str,
    fmt: str | None = None,
    res_type: str = "auto",
) -> int:
    src = Path(source_path)
    dest = Path(output_path)
    out_ext = dest.suffix.lower().lstrip(".")

    is_audio = res_type == "audio" or out_ext in ("wav", "pmw")
    if res_type == "auto":
        if out_ext in ("wav", "pmw"):
            is_audio = True
        elif out_ext in ("png", "bmp", "jpg", "jpeg", "tga", "tiff"):
            is_audio = False

    target_fmt = fmt or (out_ext if out_ext else ("wav" if is_audio else "png"))

    if is_audio:
        print(f"Converting audio '{src.name}' -> '{dest}' (format={target_fmt.upper()})...")
        converted = garex.convert_audio(src, dest, format=target_fmt)
    else:
        print(f"Converting image '{src.name}' -> '{dest}' (format={target_fmt.upper()})...")
        converted = garex.convert_image(src, dest, format=target_fmt)

    print(f"Converted: {converted}")
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
