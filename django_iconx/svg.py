from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import quote

from django.conf import settings

if TYPE_CHECKING:
    from django_iconx.conf import IconSet, IconxSettings


def discover_svgs(icon_settings: IconxSettings) -> dict[str, Path]:
    """Discover SVG files by scanning static dirs and matching against set regexes.

    Returns a dict mapping icon class names to their SVG file paths.
    The largest size variant is used as default when size subdirectories exist.
    """
    # Collect all icons, grouping size variants
    plain: dict[str, Path] = {}
    sized: dict[str, dict[int, Path]] = {}

    for svg_path, relative in _scan_all_svgs():
        match = _match_set(relative, icon_settings.sets)
        if match is None:
            continue
        icon_set, remainder = match

        size, rest = _extract_size_prefix(remainder)
        if size is not None:
            icon_name = _remainder_to_icon_name(rest, icon_set.prefix)
            if icon_name not in sized:
                sized[icon_name] = {}
            sized[icon_name][size] = svg_path
        else:
            icon_name = _remainder_to_icon_name(remainder, icon_set.prefix)
            plain[icon_name] = svg_path

    # Merge: sized icons use the largest variant as default
    icons = dict(plain)
    for icon_name, size_map in sized.items():
        largest = max(size_map)
        icons[icon_name] = size_map[largest]

    return icons


def discover_svg_variants(icon_settings: IconxSettings) -> dict[str, dict[int, Path]]:
    """Discover icons that have multiple size variants.

    Returns a dict mapping icon names to their size variants (px -> path).
    Only includes icons with 2+ size variants.
    """
    # First collect all SVGs with their size info
    raw: dict[str, dict[int, Path]] = {}

    for svg_path, relative in _scan_all_svgs():
        match = _match_set(relative, icon_settings.sets)
        if match is None:
            continue
        icon_set, remainder = match

        # Check if remainder starts with a size directory
        size, rest = _extract_size_prefix(remainder)
        if size is None:
            continue

        icon_name = _remainder_to_icon_name(rest, icon_set.prefix)
        if icon_name not in raw:
            raw[icon_name] = {}
        raw[icon_name][size] = svg_path

    return {name: sizes for name, sizes in raw.items() if len(sizes) >= 2}  # noqa: PLR2004


def discover_icon_sets(icon_settings: IconxSettings) -> dict[str, IconSet]:
    """Map each icon name to its IconSet config (for color mode lookup)."""
    result: dict[str, IconSet] = {}

    for _svg_path, relative in _scan_all_svgs():
        match = _match_set(relative, icon_settings.sets)
        if match is None:
            continue
        icon_set, remainder = match

        # Strip size prefix if present
        size, rest = _extract_size_prefix(remainder)
        name_remainder = rest if size is not None else remainder
        icon_name = _remainder_to_icon_name(name_remainder, icon_set.prefix)
        result[icon_name] = icon_set

    return result


def _scan_all_svgs() -> list[tuple[Path, str]]:
    """Scan all STATICFILES_DIRS for SVG files.

    Returns list of (absolute_path, relative_path_from_static_root) tuples.
    """
    results: list[tuple[Path, str]] = []
    seen: set[Path] = set()

    for static_dir in getattr(settings, "STATICFILES_DIRS", []):
        static_path = Path(static_dir)
        if not static_path.is_dir():
            continue
        for svg_path in sorted(static_path.glob("**/*.svg")):
            resolved = svg_path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            relative = str(svg_path.relative_to(static_path))
            results.append((svg_path, relative))

    return results


def _match_set(relative_path: str, sets: list[IconSet]) -> tuple[IconSet, str] | None:
    """Match a relative SVG path against the ordered set regexes.

    Returns (matched_set, remainder_after_match) or None.
    """
    for icon_set in sets:
        m = re.match(icon_set.path, relative_path)
        if m:
            remainder = relative_path[m.end() :]
            return icon_set, remainder
    return None


def _extract_size_prefix(remainder: str) -> tuple[int | None, str]:
    """Check if remainder starts with a numeric size directory (e.g. '24/search.svg').

    Returns (size_px, rest) or (None, remainder).
    """
    m = re.match(r"(\d+)/(.+)", remainder)
    if m:
        return int(m.group(1)), m.group(2)
    return None, remainder


def _remainder_to_icon_name(remainder: str, prefix: str) -> str:
    """Convert the remainder of a matched path to an icon class name.

    'search.svg' -> 'search'
    'sub/arrow-left.svg' -> 'sub-arrow-left'
    """
    # Strip .svg extension
    name = re.sub(r"\.svg$", "", remainder)
    # Replace path separators with dashes
    name = name.replace("/", "-").replace("\\", "-")

    if prefix:
        name = f"{prefix}-{name}"

    return name



def normalize_svg(svg_content: str, *, color: str = "mono") -> str:
    """Normalize SVG for CSS embedding.

    In ``mono`` mode (mask-image), colors are replaced with ``black`` so the
    SVG works as a luminance mask driven by ``currentColor``.

    In ``original`` mode (background-image), colors are preserved so the SVG
    renders with its own fills and strokes.

    Both modes strip XML declarations, comments, and metadata.
    """
    # Strip XML declaration
    svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content)
    # Strip comments
    svg_content = re.sub(r"<!--[\s\S]*?-->", "", svg_content)
    # Strip metadata, title, desc elements
    svg_content = re.sub(r"<(metadata|title|desc)[^>]*>[\s\S]*?</\1>", "", svg_content)

    if color == "mono":
        # Replace currentColor with black (currentColor won't resolve in data-URIs)
        svg_content = re.sub(r'(fill|stroke)="currentColor"', r'\1="black"', svg_content)
        # Remove decorative fills (not none, not black — those are structural/needed)
        svg_content = re.sub(r'\s+fill="(?!none|black)[^"]*"', "", svg_content)

    # Collapse whitespace
    return re.sub(r"\s+", " ", svg_content).strip()


def svg_to_data_uri(svg_content: str, *, color: str = "mono") -> str:
    """Convert SVG content to a URL-encoded data URI (not base64)."""
    normalized = normalize_svg(svg_content, color=color)
    encoded = quote(normalized, safe="")
    return f"data:image/svg+xml,{encoded}"
