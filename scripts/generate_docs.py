#!/usr/bin/env python3
"""Generate lane documentation pages from the current Fastfile.

Reads ``fastlane/Fastfile`` from disk, parses it with
:func:`fastfile_parser.parse_fastfile_detailed`, and writes Markdown pages
into ``docs/``.

Usage:
    python scripts/generate_docs.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# Make sure sibling modules are importable
sys.path.insert(0, str(SCRIPT_DIR))

from fastfile_parser import (  # noqa: E402
    FastfileDetails,
    LaneDetail,
    parse_fastfile_detailed,
)

FASTFILE_PATH = REPO_ROOT / "fastlane" / "Fastfile"
DOCS_DIR = REPO_ROOT / "docs"
CONTENT_DIR = DOCS_DIR / "content"

# ---------------------------------------------------------------------------
# Lane-to-file mapping
# ---------------------------------------------------------------------------

LANE_FILE_MAP: dict[str, str] = {
    "provisioning": "provisioning.md",
    "update_provisioning": "provisioning.md",
    "update_release_provisioning": "provisioning.md",
    "create_apps": "create-apps.md",
    "create_apps_for_extension": "create-apps.md",
}

PAGE_TITLE_MAP: dict[str, str] = {
    "provisioning.md": "Provisioning",
    "create-apps.md": "Create Apps",
}


def _filename_for_lane(name: str) -> str:
    """Return the target .md filename for a lane."""
    return LANE_FILE_MAP.get(name, name.replace("_", "-") + ".md")


def _page_title(filename: str, first_lane: str) -> str:
    """Return the page title for a given filename."""
    if filename in PAGE_TITLE_MAP:
        return PAGE_TITLE_MAP[filename]
    # Derive from filename: "beta.md" -> "Beta", "generate-graphql-operations.md" -> "Generate Graphql Operations"
    return filename.removesuffix(".md").replace("-", " ").title()


# ---------------------------------------------------------------------------
# Custom content loader
# ---------------------------------------------------------------------------


def _load_custom_content(subdir: str, name: str) -> str:
    """Load custom content from docs/content/{subdir}/{name}.md if it exists."""
    path = CONTENT_DIR / subdir / f"{name}.md"
    if path.is_file():
        return path.read_text().strip()
    return ""


# ---------------------------------------------------------------------------
# Lane section renderer
# ---------------------------------------------------------------------------


def _render_lane_section(lane: LaneDetail) -> str:
    """Render a single lane's documentation section."""
    lines: list[str] = []

    lines.append(f"## {lane.name}")
    lines.append("")

    if lane.description:
        # Strip the Options: metadata from the displayed description
        desc_display = lane.description
        opts_idx = desc_display.find(" Options: -")
        if opts_idx != -1:
            desc_display = desc_display[:opts_idx].rstrip()
        # Also remove trailing period for cleaner display, then re-add
        desc_display = desc_display.rstrip(".")
        lines.append(f"{desc_display}.")
        lines.append("")

    lines.append("```bash")
    lines.append(f"bundle exec fastlane {lane.name}")
    lines.append("```")
    lines.append("")

    # Options table
    if lane.options:
        lines.append("### Options")
        lines.append("")
        lines.append("| Option | Type | Description |")
        lines.append("|--------|------|-------------|")
        for opt in lane.options:
            lines.append(f"| `{opt.name}` | {opt.type} | {opt.description} |")
        lines.append("")

    # ENV vars table
    if lane.env_vars:
        lines.append("### Environment Variables")
        lines.append("")
        lines.append("| Variable |")
        lines.append("|----------|")
        for var in lane.env_vars:
            lines.append(f"| `{var}` |")
        lines.append("")

    # Custom details content
    custom = _load_custom_content("lanes", lane.name)
    if custom:
        lines.append("## Details")
        lines.append("")
        lines.append(custom)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Page generators
# ---------------------------------------------------------------------------


def _generate_lane_pages(details: FastfileDetails) -> list[str]:
    """Generate lane doc pages. Returns list of written file paths."""
    lanes_dir = DOCS_DIR / "lanes"
    lanes_dir.mkdir(parents=True, exist_ok=True)

    # Group lanes by target filename, preserving LANE_FILE_MAP order for shared
    # pages and Fastfile order for the rest.
    file_lanes: dict[str, list[LaneDetail]] = defaultdict(list)
    # First, add lanes in LANE_FILE_MAP order (for shared pages)
    map_order = list(LANE_FILE_MAP.keys())
    for name in map_order:
        if name in details.lanes:
            filename = _filename_for_lane(name)
            file_lanes[filename].append(details.lanes[name])
    # Then add remaining lanes not in LANE_FILE_MAP (Fastfile order)
    for name, lane in details.lanes.items():
        if name not in LANE_FILE_MAP:
            filename = _filename_for_lane(name)
            file_lanes[filename].append(lane)

    written: list[str] = []

    for filename, lanes in file_lanes.items():
        title = _page_title(filename, lanes[0].name)
        sections: list[str] = []

        sections.append(f"# {title}")
        sections.append("")

        for i, lane in enumerate(lanes):
            if i > 0:
                sections.append("---")
                sections.append("")
            sections.append(_render_lane_section(lane))

        page_path = lanes_dir / filename
        page_path.write_text("\n".join(sections).rstrip() + "\n")
        written.append(str(page_path.relative_to(REPO_ROOT)))

    return written


def _generate_index_page(details: FastfileDetails) -> str:
    """Generate the lanes/index.md overview page."""
    lanes_dir = DOCS_DIR / "lanes"
    lanes_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Lanes Overview",
        "",
        "This section documents all public and private lanes available in the Fastfile.",
        "",
        "## Public lanes",
        "",
        "These lanes are intended for direct execution by developers or CI.",
        "",
        "| Lane | Description |",
        "|------|-------------|",
    ]

    # Order: LANE_FILE_MAP lanes first (in map order), then remaining in Fastfile order
    ordered_names: list[str] = []
    for map_name in LANE_FILE_MAP:
        if map_name in details.lanes and map_name not in ordered_names:
            ordered_names.append(map_name)
    for name in details.lanes:
        if name not in ordered_names:
            ordered_names.append(name)

    for name in ordered_names:
        lane = details.lanes[name]
        filename = _filename_for_lane(name)
        # Clean description for the table
        desc = lane.description
        opts_idx = desc.find(" Options: -")
        if opts_idx != -1:
            desc = desc[:opts_idx].rstrip()
        desc = desc.rstrip(".")
        link = f"[`{name}`]({filename}#{name})"
        lines.append(f"| {link} | {desc} |")

    lines.append("")
    lines.append("## Private lanes")
    lines.append("")
    lines.append("These lanes are used internally by public lanes and are not meant to be called directly.")
    lines.append("")
    lines.append("| Lane | Description |")
    lines.append("|------|-------------|")

    for name, lane in details.private_lanes.items():
        desc = lane.description
        if desc:
            opts_idx = desc.find(" Options: -")
            if opts_idx != -1:
                desc = desc[:opts_idx].rstrip()
            desc = desc.rstrip(".")
        lines.append(f"| `{name}` | {desc} |")

    lines.append("")

    index_path = lanes_dir / "index.md"
    index_path.write_text("\n".join(lines).rstrip() + "\n")
    return str(index_path.relative_to(REPO_ROOT))


def _generate_env_variables_page(details: FastfileDetails) -> str:
    """Generate docs/configuration/env-variables.md — complete ENV var reference."""
    config_dir = DOCS_DIR / "configuration"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Collect all ENV vars and which lanes use them
    var_lanes: dict[str, list[str]] = defaultdict(list)

    for name, lane in details.lanes.items():
        for var in lane.env_vars:
            var_lanes[var].append(name)
    for name, lane in details.private_lanes.items():
        for var in lane.env_vars:
            var_lanes[var].append(f"{name} (private)")

    lines: list[str] = ["# Environment Variables", ""]

    # Prepend custom content if it exists
    custom = _load_custom_content("configuration", "env-variables")
    if custom:
        lines.append(custom)
        lines.append("")

    lines.append("## Variable Reference")
    lines.append("")
    lines.append("| Variable | Used by |")
    lines.append("|----------|---------|")

    for var in sorted(var_lanes.keys()):
        users = ", ".join(f"`{u}`" for u in sorted(set(var_lanes[var])))
        lines.append(f"| `{var}` | {users} |")

    lines.append("")

    page_path = config_dir / "env-variables.md"
    page_path.write_text("\n".join(lines).rstrip() + "\n")
    return str(page_path.relative_to(REPO_ROOT))


def _generate_helpers_page(details: FastfileDetails) -> str:
    """Generate docs/configuration/helpers.md — helper method reference."""
    config_dir = DOCS_DIR / "configuration"
    config_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = ["# Helper Methods", ""]

    # Prepend custom content if it exists
    custom = _load_custom_content("configuration", "helpers")
    if custom:
        lines.append(custom)
        lines.append("")

    lines.append("## Helper Reference")
    lines.append("")

    for name, helper in sorted(details.helpers.items()):
        lines.append(f"### {name}")
        lines.append("")
        if helper.env_vars:
            lines.append("**Environment Variables:**")
            lines.append("")
            lines.append("| Variable |")
            lines.append("|----------|")
            for var in helper.env_vars:
                lines.append(f"| `{var}` |")
            lines.append("")
        else:
            lines.append("No environment variables used.")
            lines.append("")

    page_path = config_dir / "helpers.md"
    page_path.write_text("\n".join(lines).rstrip() + "\n")
    return str(page_path.relative_to(REPO_ROOT))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if not FASTFILE_PATH.is_file():
        print(f"Error: Fastfile not found at {FASTFILE_PATH}", file=sys.stderr)
        sys.exit(1)

    text = FASTFILE_PATH.read_text()
    details = parse_fastfile_detailed(text)

    print(f"Parsed: {len(details.lanes)} public lanes, "
          f"{len(details.private_lanes)} private lanes, "
          f"{len(details.helpers)} helpers, "
          f"{len(details.plugins)} plugins")
    print()

    generated: list[str] = []

    # Lane pages
    lane_pages = _generate_lane_pages(details)
    generated.extend(lane_pages)

    # Index page
    index_path = _generate_index_page(details)
    generated.append(index_path)

    # ENV variables page
    env_path = _generate_env_variables_page(details)
    generated.append(env_path)

    # Helpers page
    helpers_path = _generate_helpers_page(details)
    generated.append(helpers_path)

    print("Generated files:")
    for path in sorted(generated):
        print(f"  {path}")


if __name__ == "__main__":
    main()
