from __future__ import annotations

from typing import TYPE_CHECKING

from django_iconx.svg import discover_icon_sets, discover_svg_variants, discover_svgs, svg_to_data_uri

if TYPE_CHECKING:
    from pathlib import Path

    from django_iconx.conf import IconxSettings

# Tailwind text-* classes mapped to their font-size in px.
# Used to pick the nearest icon size variant for each class.
TEXT_SIZES: list[tuple[str, int]] = [
    ("text-xs", 12),
    ("text-sm", 14),
    ("text-base", 16),
    ("text-lg", 18),
    ("text-xl", 20),
    ("text-2xl", 24),
    ("text-3xl", 30),
    ("text-4xl", 36),
    ("text-5xl", 48),
]


def generate_css(
    icon_settings: IconxSettings,
    *,
    subset: set[str] | None = None,
) -> str:
    """Generate the complete CSS file content for all configured icons."""
    icons = discover_svgs(icon_settings)
    variants = discover_svg_variants(icon_settings)
    icon_set_map = discover_icon_sets(icon_settings)

    if subset:
        icons = {name: path for name, path in icons.items() if name in subset}
        variants = {name: v for name, v in variants.items() if name in subset}

    prefix = icon_settings.prefix

    # Partition icons by color mode
    mono_names = sorted(n for n in icons if icon_set_map[n].color == "mono")
    multi_names = sorted(n for n in icons if icon_set_map[n].color == "original")

    lines = [_base_rule(prefix, icon_settings.size)]

    # Grouped mono base selector
    if mono_names:
        lines.append(_mono_base_rule(prefix, mono_names))

    # Grouped multi base selector
    if multi_names:
        lines.append(_multi_base_rule(prefix, multi_names))

    # Individual icon rules
    for icon_name, svg_path in sorted(icons.items()):
        color = icon_set_map[icon_name].color
        rule = _icon_rule(prefix, icon_name, svg_path, icon_settings.mode, color)
        if rule:
            lines.append(rule)

    # Size-variant overrides
    for icon_name, size_map in sorted(variants.items()):
        color = icon_set_map[icon_name].color
        variant_rules = _size_variant_rules(prefix, icon_name, size_map, icon_settings.mode, color)
        if variant_rules:
            lines.append(variant_rules)

    return "\n".join(lines) + "\n"


def _base_rule(prefix: str, size: str) -> str:
    return f""".{prefix} {{
  display: inline-block;
  width: {size};
  height: {size};
  vertical-align: -0.125em;
  line-height: 1;
}}"""


def _mono_base_rule(prefix: str, icon_names: list[str]) -> str:
    selectors = ",\n".join(f".{prefix}-{name}" for name in icon_names)
    return f"""
{selectors} {{
  background-color: currentColor;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  mask-mode: alpha;
}}"""


def _multi_base_rule(prefix: str, icon_names: list[str]) -> str:
    selectors = ",\n".join(f".{prefix}-{name}" for name in icon_names)
    return f"""
{selectors} {{
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}}"""


def _icon_rule(prefix: str, icon_name: str, svg_path: Path, mode: str, color: str) -> str | None:
    url = _svg_url(svg_path, mode)
    if url is None:
        return None
    prop = "background-image" if color == "original" else "mask-image"
    return f'\n.{prefix}-{icon_name} {{ {prop}: url("{url}"); }}'


def _svg_url(svg_path: Path, mode: str) -> str | None:
    if mode == "data_uri":
        svg_content = svg_path.read_text(encoding="utf-8")
        return svg_to_data_uri(svg_content)
    if mode == "url":
        return svg_path.name
    return None


def _nearest_variant(available_sizes: list[int], target_px: int) -> int:
    """Pick the available icon size closest to the target pixel size."""
    return min(available_sizes, key=lambda s: abs(s - target_px))


def _size_variant_rules(
    prefix: str,
    icon_name: str,
    size_map: dict[int, Path],
    mode: str,
    color: str,
) -> str:
    """Generate text-* override rules that swap to the optimal SVG variant."""
    available = sorted(size_map)
    largest = max(available)

    # Group text-* classes by which variant they map to
    variant_to_classes: dict[int, list[str]] = {}
    for text_class, font_px in TEXT_SIZES:
        best = _nearest_variant(available, font_px)
        if best == largest:
            continue
        if best not in variant_to_classes:
            variant_to_classes[best] = []
        variant_to_classes[best].append(text_class)

    if not variant_to_classes:
        return ""

    prop = "background-image" if color == "original" else "mask-image"
    rules: list[str] = []
    for size_px, text_classes in sorted(variant_to_classes.items()):
        url = _svg_url(size_map[size_px], mode)
        if url is None:
            continue

        selectors = ",\n".join(f".{tc}.{prefix}-{icon_name}" for tc in text_classes)
        rules.append(f"""\n{selectors} {{
  {prop}: url("{url}");
}}""")

    return "\n".join(rules)
