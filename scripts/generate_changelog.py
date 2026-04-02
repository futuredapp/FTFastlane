#!/usr/bin/env python3
"""Generate changelog by diffing Fastfile API surfaces between tags.

Usage:
    python scripts/generate_changelog.py [--ref REF]

Options:
    --ref   Git ref (e.g. refs/tags/1.0.0 or refs/heads/main).
            Controls the home page "What's New" section:
            - Tag ref  → "What's New in {tag}"
            - Branch   → "What's Going to Change"
            Defaults to HEAD.

Outputs docs/changelog.md and injects a What's New section into docs/index.md.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FASTFILE_PATH = "fastlane/Fastfile"
DOCS_DIR = REPO_ROOT / "docs"

AUTHOR_ALIASES: dict[str, str] = {
    "ssestak": "Šimon Šesták",
    "matejsemancik": "Matej Semančík",
}
AUTHOR_EXCLUDE: set[str] = {"github-actions[bot]"}

# ---------------------------------------------------------------------------
# Regex patterns for Fastfile parsing
# ---------------------------------------------------------------------------

RE_DESC = re.compile(r'^desc\s+"(.+)"')
RE_LANE = re.compile(r"^lane\s+:(\w+)\s+do")
RE_PRIVATE_LANE = re.compile(r"^private_lane\s+:(\w+)\s+do")
RE_HELPER = re.compile(r"^def\s+(\w+)")
RE_PLUGIN = re.compile(r'^fastlane_require\s+"(.+)"')
RE_ENV = re.compile(r'ENV\["(\w+)"\]')

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class LaneInfo:
    name: str
    description: str = ""
    visibility: str = "public"


@dataclass
class FastfileAPI:
    lanes: dict[str, LaneInfo] = field(default_factory=dict)
    private_lanes: dict[str, LaneInfo] = field(default_factory=dict)
    helpers: set[str] = field(default_factory=set)
    plugins: set[str] = field(default_factory=set)
    env_vars: set[str] = field(default_factory=set)


@dataclass
class FastfileDiff:
    # Breaking
    removed_lanes: list[LaneInfo] = field(default_factory=list)
    removed_env_vars: list[str] = field(default_factory=list)
    removed_plugins: list[str] = field(default_factory=list)
    # New
    added_lanes: list[LaneInfo] = field(default_factory=list)
    added_env_vars: list[str] = field(default_factory=list)
    added_plugins: list[str] = field(default_factory=list)
    # Changed
    changed_lanes: list[tuple[LaneInfo, LaneInfo]] = field(default_factory=list)
    # Internal
    added_private_lanes: list[str] = field(default_factory=list)
    removed_private_lanes: list[str] = field(default_factory=list)
    added_helpers: list[str] = field(default_factory=list)
    removed_helpers: list[str] = field(default_factory=list)
    pr_summaries: list[str] = field(default_factory=list)
    contributors: list[str] = field(default_factory=list)

    @property
    def has_breaking(self) -> bool:
        return bool(self.removed_lanes or self.removed_env_vars or self.removed_plugins)

    @property
    def has_new(self) -> bool:
        return bool(self.added_lanes or self.added_env_vars or self.added_plugins)

    @property
    def has_changes(self) -> bool:
        return bool(self.changed_lanes)

    @property
    def has_internal(self) -> bool:
        return bool(
            self.added_private_lanes
            or self.removed_private_lanes
            or self.added_helpers
            or self.removed_helpers
            or self.pr_summaries
        )

    @property
    def is_empty(self) -> bool:
        return not (self.has_breaking or self.has_new or self.has_changes or self.has_internal)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def get_sorted_tags() -> list[str]:
    raw = _git("tag", "--sort=v:refname")
    if not raw:
        return []
    return [t for t in raw.splitlines() if re.match(r"^\d+\.\d+", t)]


def get_tag_date(tag: str) -> str:
    return _git("log", "-1", "--format=%ai", tag).split(" ")[0]


def read_file_at_tag(tag: str, path: str) -> str:
    return _git("show", f"{tag}:{path}")


def _normalize_key(name: str) -> str:
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", name)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def get_contributors(old_tag: str | None, new_tag: str) -> list[str]:
    if old_tag:
        raw = _git("log", "--format=%aN", f"{old_tag}..{new_tag}")
    else:
        raw = _git("log", "--format=%aN", new_tag)
    if not raw:
        return []

    seen: dict[str, str] = {}
    for name in raw.splitlines():
        if name in AUTHOR_EXCLUDE:
            continue
        canonical = AUTHOR_ALIASES.get(name, name)
        key = _normalize_key(canonical)
        if key not in seen or len(canonical) > len(seen[key]):
            seen[key] = canonical
    return sorted(seen.values())


def get_merge_pr_summaries(old_tag: str, new_tag: str) -> list[str]:
    raw = _git(
        "log",
        "--first-parent",
        "--merges",
        "--format=%s",
        f"{old_tag}..{new_tag}",
    )
    if not raw:
        return []
    return raw.splitlines()


# ---------------------------------------------------------------------------
# Fastfile parser
# ---------------------------------------------------------------------------


def parse_fastfile(text: str) -> FastfileAPI:
    api = FastfileAPI()
    if not text:
        return api

    pending_desc = ""
    for line in text.splitlines():
        stripped = line.strip()

        m = RE_PLUGIN.match(stripped)
        if m:
            api.plugins.add(m.group(1))
            continue

        m = RE_DESC.match(stripped)
        if m:
            pending_desc = m.group(1)
            continue

        m = RE_LANE.match(stripped)
        if m:
            name = m.group(1)
            api.lanes[name] = LaneInfo(name=name, description=pending_desc, visibility="public")
            pending_desc = ""
            continue

        m = RE_PRIVATE_LANE.match(stripped)
        if m:
            name = m.group(1)
            api.private_lanes[name] = LaneInfo(name=name, description=pending_desc, visibility="private")
            pending_desc = ""
            continue

        m = RE_HELPER.match(stripped)
        if m:
            api.helpers.add(m.group(1))
            pending_desc = ""
            continue

        # Collect ENV references from any line
        for env_match in RE_ENV.finditer(line):
            api.env_vars.add(env_match.group(1))

    return api


# ---------------------------------------------------------------------------
# Diff engine
# ---------------------------------------------------------------------------


def diff_api(old: FastfileAPI, new: FastfileAPI) -> FastfileDiff:
    diff = FastfileDiff()

    # Public lanes
    for name in sorted(set(old.lanes) - set(new.lanes)):
        diff.removed_lanes.append(old.lanes[name])
    for name in sorted(set(new.lanes) - set(old.lanes)):
        diff.added_lanes.append(new.lanes[name])
    for name in sorted(set(old.lanes) & set(new.lanes)):
        if old.lanes[name].description != new.lanes[name].description:
            diff.changed_lanes.append((old.lanes[name], new.lanes[name]))

    # ENV vars
    diff.removed_env_vars = sorted(old.env_vars - new.env_vars)
    diff.added_env_vars = sorted(new.env_vars - old.env_vars)

    # Plugins
    diff.removed_plugins = sorted(old.plugins - new.plugins)
    diff.added_plugins = sorted(new.plugins - old.plugins)

    # Private lanes
    diff.removed_private_lanes = sorted(set(old.private_lanes) - set(new.private_lanes))
    diff.added_private_lanes = sorted(set(new.private_lanes) - set(old.private_lanes))

    # Helpers
    diff.removed_helpers = sorted(old.helpers - new.helpers)
    diff.added_helpers = sorted(new.helpers - old.helpers)

    return diff


def diff_tags(old_tag: str, new_tag: str) -> FastfileDiff:
    old_text = read_file_at_tag(old_tag, FASTFILE_PATH)
    new_text = read_file_at_tag(new_tag, FASTFILE_PATH)

    if old_text == new_text:
        return FastfileDiff()

    old_api = parse_fastfile(old_text)
    new_api = parse_fastfile(new_text)
    diff = diff_api(old_api, new_api)
    diff.pr_summaries = get_merge_pr_summaries(old_tag, new_tag)
    diff.contributors = get_contributors(old_tag, new_tag)
    return diff


# ---------------------------------------------------------------------------
# Public API — for home page What's New
# ---------------------------------------------------------------------------


def get_version_diff(version: str) -> tuple[str, FastfileDiff] | None:
    tags = get_sorted_tags()
    if version not in tags:
        return None
    idx = tags.index(version)
    if idx == 0:
        return None
    old_tag = tags[idx - 1]
    if _git("rev-parse", old_tag) == _git("rev-parse", version):
        return None
    diff = diff_tags(old_tag, version)
    return (old_tag, diff)


def get_head_diff() -> tuple[str, FastfileDiff] | None:
    tags = get_sorted_tags()
    if not tags:
        return None
    latest = tags[-1]
    old_text = read_file_at_tag(latest, FASTFILE_PATH)
    new_text = (REPO_ROOT / FASTFILE_PATH).read_text() if (REPO_ROOT / FASTFILE_PATH).exists() else ""
    if old_text == new_text:
        return None
    old_api = parse_fastfile(old_text)
    new_api = parse_fastfile(new_text)
    diff = diff_api(old_api, new_api)
    diff.contributors = get_contributors(latest, "HEAD")
    return (latest, diff)


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------


def _icon(change: str) -> str:
    return {
        "added": ':material-plus:{ title="Added" }',
        "removed": ':material-minus:{ title="Removed" }',
        "modified": ':material-pencil:{ title="Modified" }',
    }[change]


def render_version(
    tag: str,
    date: str,
    diff: FastfileDiff,
    api: FastfileAPI,
    is_initial: bool = False,
) -> str:
    lines: list[str] = [f"## {tag}", "", f"_{date}_", ""]

    if is_initial:
        lines.append("Initial release. Reusable Fastlane configuration for iOS CI/CD.")
        lines.append("")
        if api.lanes:
            lines.append("### Lanes")
            lines.append("")
            for lane in api.lanes.values():
                desc = f" — {lane.description}" if lane.description else ""
                lines.append(f"- `{lane.name}`{desc}")
            lines.append("")
        if api.plugins:
            lines.append("### Plugins")
            lines.append("")
            for p in sorted(api.plugins):
                lines.append(f"- `{p}`")
            lines.append("")
        if diff.contributors:
            lines.append(f"**Contributors:** {', '.join(diff.contributors)}")
            lines.append("")
        return "\n".join(lines)

    # Breaking changes
    if diff.has_breaking:
        lines.append("### Breaking changes")
        lines.append("")
        for lane in diff.removed_lanes:
            lines.append(f"- {_icon('removed')} Removed lane `{lane.name}`")
        for p in diff.removed_plugins:
            lines.append(f"- {_icon('removed')} Removed plugin `{p}`")
        for v in diff.removed_env_vars:
            lines.append(f"- {_icon('removed')} ENV var `{v}` is no longer used")
        lines.append("")

    # New
    if diff.has_new:
        lines.append("### New")
        lines.append("")
        for lane in diff.added_lanes:
            desc = f" — {lane.description}" if lane.description else ""
            lines.append(f"- {_icon('added')} Lane `{lane.name}`{desc}")
        for p in diff.added_plugins:
            lines.append(f"- {_icon('added')} Plugin `{p}`")
        for v in diff.added_env_vars:
            lines.append(f"- {_icon('added')} ENV var `{v}`")
        lines.append("")

    # Changed
    if diff.has_changes:
        lines.append("### Changed")
        lines.append("")
        for old_lane, new_lane in diff.changed_lanes:
            lines.append(f"- {_icon('modified')} Lane `{new_lane.name}` — description updated")
        lines.append("")

    # Internal
    if diff.has_internal:
        lines.append("### Internal changes")
        lines.append("")
        for name in diff.added_private_lanes:
            lines.append(f"- Added private lane `{name}`")
        for name in diff.removed_private_lanes:
            lines.append(f"- Removed private lane `{name}`")
        for name in diff.added_helpers:
            lines.append(f"- Added helper `{name}`")
        for name in diff.removed_helpers:
            lines.append(f"- Removed helper `{name}`")
        for summary in diff.pr_summaries:
            lines.append(f"- {summary}")
        lines.append("")

    # Contributors
    if diff.contributors:
        lines.append(f"**Contributors:** {', '.join(diff.contributors)}")
        lines.append("")

    return "\n".join(lines)


def render_whats_new(title: str, diff: FastfileDiff) -> str:
    """Render the What's New / What's Going to Change section for the home page."""
    lines: list[str] = ["---", "", f"## {title}", ""]

    if diff.has_breaking:
        lines.append('!!! danger "Breaking Changes"')
        lines.append("")
        for lane in diff.removed_lanes:
            lines.append(f"    - Removed lane `{lane.name}`")
        for p in diff.removed_plugins:
            lines.append(f"    - Removed plugin `{p}`")
        for v in diff.removed_env_vars:
            lines.append(f"    - ENV var `{v}` is no longer used")
        lines.append("")

    if diff.has_new:
        lines.append("### New")
        lines.append("")
        for lane in diff.added_lanes:
            desc = f" — {lane.description}" if lane.description else ""
            lines.append(f"- {_icon('added')} Lane `{lane.name}`{desc}")
        for p in diff.added_plugins:
            lines.append(f"- {_icon('added')} Plugin `{p}`")
        for v in diff.added_env_vars:
            lines.append(f"- {_icon('added')} ENV var `{v}`")
        lines.append("")

    if diff.has_changes:
        lines.append("### Changed")
        lines.append("")
        for old_lane, new_lane in diff.changed_lanes:
            lines.append(f"- {_icon('modified')} Lane `{new_lane.name}` — description updated")
        lines.append("")

    lines.append("[:octicons-arrow-right-24: Full Changelog](changelog.md)")
    lines.append("")
    lines.append("---")

    return "\n".join(lines)


def inject_whats_new(index_path: Path, content: str) -> None:
    """Replace content between WHATS_NEW markers in index.md."""
    text = index_path.read_text()
    start_marker = "<!-- WHATS_NEW_START -->"
    end_marker = "<!-- WHATS_NEW_END -->"

    if start_marker not in text or end_marker not in text:
        print(f"  Warning: markers not found in {index_path}, skipping injection")
        return

    before = text[: text.index(start_marker) + len(start_marker)]
    after = text[text.index(end_marker) :]

    if content:
        new_text = before + "\n" + content + "\n" + after
    else:
        new_text = before + "\n" + after

    index_path.write_text(new_text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate changelog for ios-fastlane")
    parser.add_argument(
        "--ref",
        default="HEAD",
        help="Git ref (e.g. refs/tags/1.0.0 or refs/heads/main)",
    )
    args = parser.parse_args()

    tags = get_sorted_tags()

    # --- Generate full changelog ---
    if not tags:
        print("No version tags found.")
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        (DOCS_DIR / "changelog.md").write_text("# Changelog\n\nNo releases yet.\n")
        inject_whats_new(DOCS_DIR / "index.md", "")
        return

    print(f"Found {len(tags)} tags: {', '.join(tags)}")
    entries: list[str] = []

    for i, tag in enumerate(tags):
        date = get_tag_date(tag)

        if i == 0:
            api = parse_fastfile(read_file_at_tag(tag, FASTFILE_PATH))
            contributors = get_contributors(None, tag)
            diff = FastfileDiff(contributors=contributors)
            entries.append(render_version(tag, date, diff, api, is_initial=True))
        else:
            old_tag = tags[i - 1]
            if _git("rev-parse", old_tag) == _git("rev-parse", tag):
                entries.append(f"## {tag}\n\n_{date}_\n\nSame as {old_tag} (re-tagged).\n")
                continue
            diff = diff_tags(old_tag, tag)
            api = parse_fastfile(read_file_at_tag(tag, FASTFILE_PATH))
            entries.append(render_version(tag, date, diff, api))

        print(f"  Generated: {tag}")

    header = "# Changelog\n\nAll notable changes to Futured iOS Fastlane.\n\n"
    output = header + "\n---\n\n".join(reversed(entries))

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    changelog_path = DOCS_DIR / "changelog.md"
    changelog_path.write_text(output)
    print(f"\nWritten: {changelog_path.relative_to(REPO_ROOT)}")

    # --- Inject What's New into home page ---
    ref = args.ref
    is_tag = ref.startswith("refs/tags/")

    if is_tag:
        tag_name = ref.removeprefix("refs/tags/")
        result = get_version_diff(tag_name)
        if result:
            _, diff = result
            if not diff.is_empty:
                whats_new = render_whats_new(f"What's New in {tag_name}", diff)
                inject_whats_new(DOCS_DIR / "index.md", whats_new)
                print(f"  Injected: What's New in {tag_name}")
                return
        # First tag or no changes — no What's New section
        inject_whats_new(DOCS_DIR / "index.md", "")
    else:
        result = get_head_diff()
        if result:
            _, diff = result
            if not diff.is_empty:
                whats_new = render_whats_new("What's Going to Change", diff)
                inject_whats_new(DOCS_DIR / "index.md", whats_new)
                print("  Injected: What's Going to Change")
                return
        inject_whats_new(DOCS_DIR / "index.md", "")


if __name__ == "__main__":
    main()
