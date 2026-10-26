"""Format inventory script for GarEx.

Generates docs/FORMAT_TRACKER.md from the exported formats inventory (tools/formats_inventory.json).
"""

from __future__ import annotations

import json
from pathlib import Path

NATIVE_FORMATS = {"RPA", "XP3", "INT", "SAR", "NSA"}


def generate_tracker() -> None:
    root = Path(__file__).resolve().parent.parent
    json_path = root / "tools" / "formats_inventory.json"
    tracker_path = root / "docs" / "FORMAT_TRACKER.md"

    if not json_path.exists():
        raise FileNotFoundError(f"Inventory JSON not found at {json_path}. Run tools/export_inventory.ps1 first.")

    with json_path.open("r", encoding="utf-8-sig") as f:
        formats = json.load(f)

    # Sort formats by kind then Tag
    formats.sort(key=lambda x: (x.get("Kind", ""), x.get("Tag", "")))

    lines = [
        "# Format Tracker",
        "",
        "This table tracks all 800+ visual novel archive, image, audio, and script formats recognized by GarEx.",
        "",
        "| Format | Kind | Ext | Upstream class | Extract | Convert | Create | Status | Notes |",
        "|---|---|---|---|:---:|:---:|:---:|:---:|---|",
    ]

    archives_count = 0
    images_count = 0
    audio_count = 0
    scripts_count = 0
    can_create_count = 0
    native_count = 0

    for fmt in formats:
        tag = (fmt.get("Tag") or "").replace("|", "\\|")
        kind = fmt.get("Kind", "")
        if kind == "archive":
            archives_count += 1
        elif kind == "image":
            images_count += 1
        elif kind == "audio":
            audio_count += 1
        elif kind == "script":
            scripts_count += 1

        ext = (fmt.get("Extensions") or "").replace("|", "\\|")
        cls_name = fmt.get("ClassName", "")
        can_extract = "yes" if fmt.get("CanExtract") else "-"
        can_convert = "yes" if fmt.get("CanConvert") else "-"
        can_create = "yes" if fmt.get("CanCreate") else "-"
        if fmt.get("CanCreate"):
            can_create_count += 1

        if tag in NATIVE_FORMATS:
            status = "native"
            native_count += 1
        else:
            status = "bridge"

        lines.append(
            f"| `{tag}` | {kind} | {ext} | `{cls_name}` | {can_extract} | {can_convert} | {can_create} | {status} | {fmt.get('Description', '').replace('|', '\\|')} |"
        )

    bridge_count = len(formats) - native_count

    lines.extend([
        "",
        "## Summary",
        f"- **Total formats**: {len(formats)}",
        f"  - **Archives**: {archives_count}",
        f"  - **Images**: {images_count}",
        f"  - **Audio**: {audio_count}",
        f"  - **Scripts**: {scripts_count}",
        f"  - **Supports packing/creation**: {can_create_count}",
        "- **Status distribution**:",
        f"  - `native`: {native_count} (Pure Python cross-platform)",
        f"  - `bridge`: {bridge_count} (via compiled GARbro assemblies)",
        "  - `native-partial`: 0",
        "",
    ])

    tracker_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Successfully generated {tracker_path} with {len(formats)} formats.")


if __name__ == "__main__":
    generate_tracker()
