from __future__ import annotations

from typing import TYPE_CHECKING

from django_iconx.svg import discover_svg_variants, discover_svgs, svg_to_data_uri

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

    if subset:
        icons = {name: path for name, path in icons.items() if name in subset}
        variants = {name: v for name, v in variants.items() if name in subset}

    prefix = icon_settings.prefix
    lines = [_base_rule(prefix, icon_settings.size)]

    for icon_name, svg_path in sorted(icons.items()):
        rule = _icon_rule(prefix, icon_name, svg_path, icon_settings.mode)
        if rule:
            lines.append(rule)

    # Generate size-variant overrides
    for icon_name, size_map in sorted(variants.items()):
        variant_rules = _size_variant_rules(prefix, icon_name, size_map, icon_settings.mode)
        if variant_rules:
            lines.append(variant_rules)

    return "\n".join(lines) + "\n"


def _base_rule(prefix: str, size: str) -> str:
    return f""".{prefix}::before {{
  display: inline-block;
  width: {size};
  height: {size};
  content: "";
  background: currentColor;
  vertical-align: middle;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
}}"""


def _icon_rule(prefix: str, icon_name: str, svg_path: Path, mode: str) -> str | None:
    if mode == "data_uri":
        svg_content = svg_path.read_text(encoding="utf-8")
        data_uri = svg_to_data_uri(svg_content)
        return f"""\n.{prefix}-{icon_name}::before {{
  mask-image: url("{data_uri}");
}}"""
    if mode == "url":
        return f"""\n.{prefix}-{icon_name}::before {{
  mask-image: url("{svg_path.name}");
}}"""
    return None


def _nearest_variant(available_sizes: list[int], target_px: int) -> int:
    """Pick the available icon size closest to the target pixel size."""
    return min(available_sizes, key=lambda s: abs(s - target_px))


def _size_variant_rules(prefix: str, icon_name: str, size_map: dict[int, Path], mode: str) -> str:
    """Generate text-* override rules that swap to the optimal SVG variant."""
    available = sorted(size_map)
    largest = max(available)

    # Group text-* classes by which variant they map to
    variant_to_classes: dict[int, list[str]] = {}
    for text_class, font_px in TEXT_SIZES:
        best = _nearest_variant(available, font_px)
        if best == largest:
            # Default rule already uses the largest — no override needed
            continue
        if best not in variant_to_classes:
            variant_to_classes[best] = []
        variant_to_classes[best].append(text_class)

    if not variant_to_classes:
        return ""

    rules: list[str] = []
    for size_px, text_classes in sorted(variant_to_classes.items()):
        svg_path = size_map[size_px]
        if mode == "data_uri":
            svg_content = svg_path.read_text(encoding="utf-8")
            data_uri = svg_to_data_uri(svg_content)
            mask_value = f'url("{data_uri}")'
        elif mode == "url":
            mask_value = f'url("{svg_path.name}")'
        else:
            continue

        selectors = ",\n".join(f".{tc}.{prefix}-{icon_name}::before" for tc in text_classes)
        rules.append(f"""\n{selectors} {{
  mask-image: {mask_value};
}}""")

    return "\n".join(rules)
