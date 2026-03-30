from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import quote

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static

if TYPE_CHECKING:
    from django_iconx.conf import IconxSettings


def discover_svgs(icon_settings: IconxSettings) -> dict[str, Path]:
    """Discover SVG files from configured icon sets.

    Returns a dict mapping icon class names (e.g. "search", "hero-arrow-left")
    to their SVG file paths. When size subdirectories exist (e.g. ``16/``, ``24/``),
    the largest variant is used as the default.
    """
    icons: dict[str, Path] = {}

    for set_prefix, directory in icon_settings.sets.items():
        resolved = _resolve_directory(directory)
        if resolved is None:
            continue

        size_dirs = _detect_size_dirs(resolved)

        if size_dirs:
            # Size-variant mode: numeric subdirectories contain size-specific SVGs
            for icon_name, variants in _collect_size_variants(size_dirs, set_prefix).items():
                # Use the largest variant as default
                largest_size = max(variants)
                icons[icon_name] = variants[largest_size]
        else:
            # Flat mode: all SVGs in one directory
            for svg_path in sorted(resolved.glob("**/*.svg")):
                icon_name = _path_to_icon_name(svg_path, resolved, set_prefix)
                icons[icon_name] = svg_path

    return icons


def discover_svg_variants(icon_settings: IconxSettings) -> dict[str, dict[int, Path]]:
    """Discover icons that have multiple size variants.

    Returns a dict mapping icon names to their size variants (px -> path).
    Only includes icons with 2+ size variants.
    """
    variants: dict[str, dict[int, Path]] = {}

    for set_prefix, directory in icon_settings.sets.items():
        resolved = _resolve_directory(directory)
        if resolved is None:
            continue

        size_dirs = _detect_size_dirs(resolved)
        if not size_dirs:
            continue

        variants.update({
            icon_name: size_map
            for icon_name, size_map in _collect_size_variants(size_dirs, set_prefix).items()
            if len(size_map) >= 2  # noqa: PLR2004
        })

    return variants


def _detect_size_dirs(root: Path) -> dict[int, Path]:
    """Detect numeric subdirectories (e.g. 16/, 20/, 24/) as size directories."""
    size_dirs: dict[int, Path] = {}
    for child in root.iterdir():
        if child.is_dir():
            try:
                size = int(child.name)
            except ValueError:
                continue
            # Only treat as size dir if it contains SVGs
            if any(child.glob("*.svg")):
                size_dirs[size] = child
    return size_dirs


def _collect_size_variants(
    size_dirs: dict[int, Path],
    set_prefix: str,
) -> dict[str, dict[int, Path]]:
    """Collect all size variants for each icon across size directories."""
    result: dict[str, dict[int, Path]] = {}

    for size_px, size_dir in sorted(size_dirs.items()):
        for svg_path in sorted(size_dir.glob("**/*.svg")):
            # Icon name from path relative to the size dir (not root)
            icon_name = _path_to_icon_name(svg_path, size_dir, set_prefix)
            if icon_name not in result:
                result[icon_name] = {}
            result[icon_name][size_px] = svg_path

    return result


def _path_to_icon_name(svg_path: Path, base_dir: Path, set_prefix: str) -> str:
    """Convert a SVG file path to an icon class name."""
    relative = svg_path.relative_to(base_dir)
    parts = list(relative.parts)
    parts[-1] = relative.stem  # strip .svg
    icon_name = "-".join(parts)

    if set_prefix:
        icon_name = f"{set_prefix}-{icon_name}"

    return icon_name


def _resolve_directory(directory: str) -> Path | None:
    """Resolve an icon directory, checking staticfiles finders and STATICFILES_DIRS."""
    # Try as a staticfiles path first
    result = find_static(directory)
    if result:
        p = Path(result) if isinstance(result, str) else Path(result[0])
        if p.is_dir():
            return p

    # Try relative to STATICFILES_DIRS
    for static_dir in getattr(settings, "STATICFILES_DIRS", []):
        candidate = Path(static_dir) / directory
        if candidate.is_dir():
            return candidate

    # Try relative to BASE_DIR
    base_dir = getattr(settings, "BASE_DIR", None)
    if base_dir:
        candidate = Path(base_dir) / directory
        if candidate.is_dir():
            return candidate

    # Try as absolute path
    candidate = Path(directory)
    if candidate.is_dir():
        return candidate

    return None


def normalize_svg(svg_content: str) -> str:
    """Normalize SVG for use with CSS mask-image.

    For mask-image, the SVG is rendered as a bitmap where black = visible and
    transparent = hidden. ``currentColor`` won't resolve inside a data-URI,
    so we replace color attributes with ``black`` to ensure visibility.

    - Strips XML declarations and comments
    - Removes metadata elements
    - Replaces ``currentColor`` in fill/stroke with ``black``
    - Removes non-``none``, non-``currentColor`` fills (decorative colors)
    """
    # Strip XML declaration
    svg_content = re.sub(r"<\?xml[^?]*\?>", "", svg_content)
    # Strip comments
    svg_content = re.sub(r"<!--[\s\S]*?-->", "", svg_content)
    # Strip metadata, title, desc elements
    svg_content = re.sub(r"<(metadata|title|desc)[^>]*>[\s\S]*?</\1>", "", svg_content)
    # Replace currentColor with black (currentColor won't resolve in data-URIs)
    svg_content = re.sub(r'(fill|stroke)="currentColor"', r'\1="black"', svg_content)
    # Remove decorative fills (not none, not black — those are structural/needed)
    svg_content = re.sub(r'\s+fill="(?!none|black)[^"]*"', "", svg_content)
    # Collapse whitespace
    return re.sub(r"\s+", " ", svg_content).strip()


def svg_to_data_uri(svg_content: str) -> str:
    """Convert SVG content to a URL-encoded data URI (not base64)."""
    normalized = normalize_svg(svg_content)
    encoded = quote(normalized, safe="")
    return f"data:image/svg+xml,{encoded}"
