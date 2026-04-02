#!/usr/bin/env python3
"""Shared Fastfile parser module.

Provides both a simple parser (backward-compatible with generate_changelog.py)
and a detailed parser that extracts per-lane options, ENV vars, and helper
dependencies with transitive resolution.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Regex patterns for Fastfile parsing
# ---------------------------------------------------------------------------

RE_DESC = re.compile(r'^desc\s+"(.+)"')
RE_LANE = re.compile(r"^lane\s+:(\w+)\s+do")
RE_PRIVATE_LANE = re.compile(r"^private_lane\s+:(\w+)\s+do")
RE_HELPER = re.compile(r"^def\s+(\w+)")
RE_PLUGIN = re.compile(r'^fastlane_require\s+"(.+)"')
RE_ENV = re.compile(r'ENV\["(\w+)"\]')
RE_OPTIONS = re.compile(r"options\[:(\w+)\]")

# ---------------------------------------------------------------------------
# Simple data structures (backward-compatible)
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


# ---------------------------------------------------------------------------
# Detailed data structures
# ---------------------------------------------------------------------------


@dataclass
class OptionInfo:
    name: str
    type: str = ""
    description: str = ""


@dataclass
class LaneDetail:
    name: str
    description: str = ""
    visibility: str = "public"
    options: list[OptionInfo] = field(default_factory=list)
    env_vars: list[str] = field(default_factory=list)


@dataclass
class HelperDetail:
    name: str
    env_vars: list[str] = field(default_factory=list)


@dataclass
class FastfileDetails:
    lanes: dict[str, LaneDetail] = field(default_factory=dict)
    private_lanes: dict[str, LaneDetail] = field(default_factory=dict)
    helpers: dict[str, HelperDetail] = field(default_factory=dict)
    plugins: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Simple parser (backward-compatible)
# ---------------------------------------------------------------------------


def parse_fastfile(text: str) -> FastfileAPI:
    """Parse a Fastfile into a simple API surface description."""
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
            api.lanes[name] = LaneInfo(
                name=name, description=pending_desc, visibility="public"
            )
            pending_desc = ""
            continue

        m = RE_PRIVATE_LANE.match(stripped)
        if m:
            name = m.group(1)
            api.private_lanes[name] = LaneInfo(
                name=name, description=pending_desc, visibility="private"
            )
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
# Desc option parser
# ---------------------------------------------------------------------------

_RE_DESC_OPTIONS = re.compile(r"-\s+(\w+):\s+(\w+)\.\s+(.+?)(?=;\s+-\s|$)")


def parse_desc_options(desc: str) -> list[OptionInfo]:
    """Parse option metadata from a desc string.

    Expects format like:
        "... Options: - name: Type. Description.; - name2: Type2. Description2."
    """
    options: list[OptionInfo] = []
    for m in _RE_DESC_OPTIONS.finditer(desc):
        options.append(
            OptionInfo(
                name=m.group(1),
                type=m.group(2),
                description=m.group(3).strip().rstrip('."'),
            )
        )
    return options


# ---------------------------------------------------------------------------
# Detailed parser
# ---------------------------------------------------------------------------

# Helpers whose ENV vars should be transitively added to calling lanes
_SETTINGS_HELPERS = {"build_settings", "code_signing_settings", "tests_settings"}


def parse_fastfile_detailed(text: str) -> FastfileDetails:
    """Parse a Fastfile into detailed lane/helper/plugin info.

    Tracks Ruby block nesting to attribute ENV vars and options to their
    containing lane or helper definition.  After the initial pass, resolves
    transitive ENV vars from settings helpers.
    """
    details = FastfileDetails()
    if not text:
        return details

    pending_desc = ""
    # Current block tracking
    current_kind: str | None = None  # "lane", "private_lane", "def"
    current_name: str | None = None
    nesting = 0
    block_env_vars: set[str] = set()
    block_option_keys: set[str] = set()
    block_helper_calls: set[str] = set()

    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()

        # --- Top-level: plugins ---
        m = RE_PLUGIN.match(stripped)
        if m:
            details.plugins.append(m.group(1))
            continue

        # --- Top-level: desc ---
        m = RE_DESC.match(stripped)
        if m:
            pending_desc = m.group(1)
            continue

        # --- Block openers: lane / private_lane / def ---
        if current_kind is None:
            m = RE_LANE.match(stripped)
            if m:
                current_kind = "lane"
                current_name = m.group(1)
                nesting = 1
                block_env_vars = set()
                block_option_keys = set()
                block_helper_calls = set()
                # Collect ENV vars from this opening line too
                for env_m in RE_ENV.finditer(line):
                    block_env_vars.add(env_m.group(1))
                for opt_m in RE_OPTIONS.finditer(line):
                    block_option_keys.add(opt_m.group(1))
                # Store desc and options parsed from desc
                desc = pending_desc
                pending_desc = ""
                options = parse_desc_options(desc)
                detail = LaneDetail(
                    name=current_name,
                    description=desc,
                    visibility="public",
                    options=options,
                )
                details.lanes[current_name] = detail
                continue

            m = RE_PRIVATE_LANE.match(stripped)
            if m:
                current_kind = "private_lane"
                current_name = m.group(1)
                nesting = 1
                block_env_vars = set()
                block_option_keys = set()
                block_helper_calls = set()
                for env_m in RE_ENV.finditer(line):
                    block_env_vars.add(env_m.group(1))
                for opt_m in RE_OPTIONS.finditer(line):
                    block_option_keys.add(opt_m.group(1))
                desc = pending_desc
                pending_desc = ""
                options = parse_desc_options(desc)
                detail = LaneDetail(
                    name=current_name,
                    description=desc,
                    visibility="private",
                    options=options,
                )
                details.private_lanes[current_name] = detail
                continue

            m = RE_HELPER.match(stripped)
            if m:
                current_kind = "def"
                current_name = m.group(1)
                nesting = 1
                block_env_vars = set()
                block_option_keys = set()
                block_helper_calls = set()
                for env_m in RE_ENV.finditer(line):
                    block_env_vars.add(env_m.group(1))
                pending_desc = ""
                details.helpers[current_name] = HelperDetail(name=current_name)
                continue

        # --- Inside a block: track nesting ---
        if current_kind is not None:
            # Collect ENV and options from this line
            for env_m in RE_ENV.finditer(line):
                block_env_vars.add(env_m.group(1))
            for opt_m in RE_OPTIONS.finditer(line):
                block_option_keys.add(opt_m.group(1))

            # Check for helper calls (settings helpers)
            for helper_name in _SETTINGS_HELPERS:
                if helper_name in stripped:
                    # Make sure it looks like a method call, not a variable
                    # assignment of the same name in a def block
                    if current_kind != "def" or current_name != helper_name:
                        block_helper_calls.add(helper_name)

            # Count nesting changes on this line
            delta = _nesting_delta(stripped)
            nesting += delta

            # Block closed?
            if nesting <= 0:
                _finalize_block(
                    details,
                    current_kind,
                    current_name,
                    block_env_vars,
                    block_helper_calls,
                )
                current_kind = None
                current_name = None
                nesting = 0

    # Resolve transitive ENV vars from settings helpers
    _resolve_transitive_env(details)

    # Sort plugins
    details.plugins = sorted(set(details.plugins))

    return details


def _nesting_delta(stripped: str) -> int:
    """Compute the nesting level change for a single stripped line.

    Ruby nesting rules relevant to Fastfile parsing:
    - ``lane :name do`` / ``private_lane :name do`` / ``def name`` open blocks
      (handled by the caller before this function is invoked)
    - ``begin`` opens a block
    - ``do`` at end of line opens a block (e.g. ``.each do |x|``)
    - ``if``/``unless`` at the *start* of a stripped line open blocks
    - ``if ... then`` at end of line also opens a block (counted via the
      leading ``if``, not double-counted via ``then``)
    - Inline ``if``/``unless`` (modifier form after other code) do NOT open
      blocks
    - ``end`` closes a block
    - ``else``, ``elsif``, ``ensure`` do not change nesting
    - Inline ``{ ... }`` blocks are net zero
    """
    delta = 0

    # Check for `begin`
    if stripped == "begin" or stripped.startswith("begin "):
        delta += 1

    # Check for `do` at end of line (block opener)
    # Matches: `... do`, `... do |options|`, `... do |x|`
    if re.search(r"\bdo\s*(\|[^|]*\|)?\s*$", stripped):
        delta += 1

    # Check for `if` / `unless` at the START of the line (block form).
    # The modifier form (e.g. `cocoapods(...) if File.exist?(...)`) does NOT
    # open a block — it has code before the keyword.
    # We also must avoid double-counting `if ... then` (the `if` already
    # counts it, so we do NOT separately count `then`).
    if re.match(r"^(if|unless)\b", stripped):
        delta += 1
    # Inline `if ... then` at end — already covered by the leading `if` match
    # above when the `if` is at the start.  For `version = if ...` form, the
    # `if` is NOT at the start, so we need to detect mid-line `if` that opens
    # a block.  However, `version = if ...` is actually a block-form if used
    # with a matching `end`.  Let's handle this: if the line contains ` if `
    # (not at start) followed by no `then` and the keyword is used as a value
    # expression, it still opens a block.  A pragmatic approach: if the line
    # ends with `then`, the block-if already started.  Otherwise, for
    # mid-line `if`, we check if `if` appears as an expression start (after
    # `=` or `(`) which also opens a block.
    elif re.search(r"[=(]\s*if\b", stripped):
        delta += 1

    # Check for standalone `end`
    if stripped == "end" or re.match(r"^end\b", stripped):
        delta -= 1

    return delta


def _finalize_block(
    details: FastfileDetails,
    kind: str | None,
    name: str | None,
    env_vars: set[str],
    helper_calls: set[str],
) -> None:
    """Store collected env_vars on the appropriate detail object."""
    if kind is None or name is None:
        return

    sorted_env = sorted(env_vars)

    if kind == "lane" and name in details.lanes:
        details.lanes[name].env_vars = sorted_env
    elif kind == "private_lane" and name in details.private_lanes:
        details.private_lanes[name].env_vars = sorted_env
    elif kind == "def" and name in details.helpers:
        details.helpers[name].env_vars = sorted_env

    # Store helper calls for later transitive resolution
    if kind in ("lane", "private_lane"):
        target = details.lanes.get(name) or details.private_lanes.get(name)
        if target is not None:
            target._helper_calls = helper_calls  # type: ignore[attr-defined]


def _resolve_transitive_env(details: FastfileDetails) -> None:
    """Add ENV vars from called settings helpers to each lane."""
    all_lanes = list(details.lanes.values()) + list(details.private_lanes.values())
    for lane in all_lanes:
        helper_calls: set[str] = getattr(lane, "_helper_calls", set())
        if not helper_calls:
            continue
        extra_env: set[str] = set()
        for helper_name in helper_calls:
            helper = details.helpers.get(helper_name)
            if helper:
                extra_env.update(helper.env_vars)
        if extra_env:
            combined = set(lane.env_vars) | extra_env
            lane.env_vars = sorted(combined)
        # Clean up the temporary attribute
        if hasattr(lane, "_helper_calls"):
            del lane._helper_calls  # type: ignore[attr-defined]
