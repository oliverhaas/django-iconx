from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import quote

from django.conf import settings

logger = logging.getLogger("django_iconx")

if TYPE_CHECKING:
    from django_iconx.conf import IconSet, IconxSettings


@dataclass
class DiscoveredIcons:
    """Result of a single discovery pass over all configured icon sets."""

    icons: dict[str, Path] = field(default_factory=dict)
    relatives: dict[str, str] = field(default_factory=dict)
    variants: dict[str, dict[int, Path]] = field(default_factory=dict)
    variant_relatives: dict[str, dict[int, str]] = field(default_factory=dict)
    icon_sets: dict[str, IconSet] = field(default_factory=dict)


def discover(icon_settings: IconxSettings, *, skip_collisions: bool = False) -> DiscoveredIcons:  # noqa: C901, PLR0912
    """Discover all SVG icons in a single filesystem scan.

    Returns a DiscoveredIcons with icons, their relative paths, size variants,
    and the IconSet each icon belongs to.

    If skip_collisions is True, name collisions log a warning and keep the first
    match. Otherwise, collisions raise ValueError.
    """
    plain: dict[str, Path] = {}
    plain_rel: dict[str, str] = {}
    sized: dict[str, dict[int, Path]] = {}
    sized_rel: dict[str, dict[int, str]] = {}
    icon_set_map: dict[str, IconSet] = {}

    for svg_path, relative in _scan_all_svgs():
        match = _match_set(relative, icon_settings.sets)
        if match is None:
            continue
        icon_set, remainder = match

        size, rest = _extract_size_prefix(remainder)
        if size is not None:
            icon_name = _remainder_to_icon_name(rest, icon_set.prefix, include_path=icon_set.include_path)
            if icon_name not in sized:
                sized[icon_name] = {}
                sized_rel[icon_name] = {}
            if size in sized[icon_name]:
                msg = f"Icon name collision: '{icon_name}' size {size} produced by both '{sized[icon_name][size]}' and '{svg_path}'. Use include_path or prefix in your ICONX sets config to disambiguate."
                if not skip_collisions:
                    raise ValueError(msg)
                logger.warning(msg)
                continue
            sized[icon_name][size] = svg_path
            sized_rel[icon_name][size] = relative
        else:
            icon_name = _remainder_to_icon_name(remainder, icon_set.prefix, include_path=icon_set.include_path)
            if icon_name in plain:
                msg = f"Icon name collision: '{icon_name}' produced by both '{plain[icon_name]}' and '{svg_path}'. Use include_path or prefix in your ICONX sets config to disambiguate."
                if not skip_collisions:
                    raise ValueError(msg)
                logger.warning(msg)
                continue
            plain[icon_name] = svg_path
            plain_rel[icon_name] = relative

        icon_set_map[icon_name] = icon_set

    # Check for collisions between plain and sized icons
    for icon_name in sized:
        if icon_name in plain:
            msg = f"Icon name collision: '{icon_name}' exists as both a plain icon and a sized variant. Use include_path or prefix in your ICONX sets config to disambiguate."
            if not skip_collisions:
                raise ValueError(msg)
            logger.warning(msg)

    # Merge: sized icons use the largest variant as default (skip collisions with plain)
    icons = dict(plain)
    relatives = dict(plain_rel)
    for icon_name, size_map in sized.items():
        if icon_name in plain:
            continue
        largest = max(size_map)
        icons[icon_name] = size_map[largest]
        relatives[icon_name] = sized_rel[icon_name][largest]

    # Filter variants to 2+ sizes only (skip collisions with plain)
    variants = {name: sizes for name, sizes in sized.items() if len(sizes) >= 2 and name not in plain}  # noqa: PLR2004
    variant_rels = {name: sized_rel[name] for name in variants}

    return DiscoveredIcons(
        icons=icons,
        relatives=relatives,
        variants=variants,
        variant_relatives=variant_rels,
        icon_sets=icon_set_map,
    )


def _scan_all_svgs() -> list[tuple[Path, str]]:
    """Scan all STATICFILES_DIRS for SVG files, following symlinks.

    Returns list of (absolute_path, relative_path_from_static_root) tuples.
    """
    results: list[tuple[Path, str]] = []
    seen: set[Path] = set()

    for static_dir in getattr(settings, "STATICFILES_DIRS", []):
        # Django allows STATICFILES_DIRS entries to be (prefix, path) tuples
        raw_path = static_dir[1] if isinstance(static_dir, (list, tuple)) else static_dir
        static_path = Path(raw_path)
        if not static_path.is_dir():
            continue
        for dirpath, _dirnames, filenames in os.walk(static_path, followlinks=True):
            for filename in sorted(filenames):
                if not filename.endswith(".svg"):
                    continue
                svg_path = Path(dirpath) / filename
                resolved = svg_path.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                relative = str(svg_path.relative_to(static_path))
                results.append((svg_path, relative))

    return sorted(results, key=lambda x: x[1])


def _match_set(relative_path: str, sets: list[IconSet]) -> tuple[IconSet, str] | None:
    """Match a relative SVG path against the ordered set regexes.

    Returns (matched_set, remainder_after_match) or None.
    """
    for icon_set in sets:
        try:
            m = re.match(icon_set.path, relative_path)
        except re.error as e:
            msg = f"Invalid regex in icon set path {icon_set.path!r}: {e}"
            raise ValueError(msg) from e
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


def _remainder_to_icon_name(remainder: str, prefix: str, *, include_path: bool = False) -> str:
    """Convert the remainder of a matched path to an icon class name.

    Default (include_path=False): 'sub/arrow-left.svg' -> 'arrow-left'
    With include_path=True:       'sub/arrow-left.svg' -> 'sub-arrow-left'
    """
    if include_path:
        name = re.sub(r"\.svg$", "", remainder)
        name = name.replace("/", "-").replace("\\", "-")
    else:
        filename = remainder.rsplit("/", 1)[-1]
        name = re.sub(r"\.svg$", "", filename)

    if prefix:
        name = f"{prefix}-{name}"

    return name


def normalize_svg(svg_content: str) -> str:
    """Normalize SVG for data-URI embedding.

    Strips XML declarations, comments, and metadata elements.
    Collapses whitespace.
    """
    svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content)
    svg_content = re.sub(r"<!--[\s\S]*?-->", "", svg_content)
    svg_content = re.sub(r"<(metadata|title|desc)[^>]*>[\s\S]*?</\1>", "", svg_content)
    return re.sub(r"\s+", " ", svg_content).strip()


def svg_to_data_uri(svg_content: str) -> str:
    """Convert SVG content to a URL-encoded data URI (not base64)."""
    normalized = normalize_svg(svg_content)
    encoded = quote(normalized, safe="")
    return f"data:image/svg+xml,{encoded}"
