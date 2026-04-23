from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings

from django_iconx.svg import DiscoveredIcons, discover, svg_to_data_uri

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
    discovered: DiscoveredIcons | None = None,
) -> str:
    """Generate the complete CSS file content for all configured icons."""
    if discovered is None:
        discovered = discover(icon_settings)

    icons = discovered.icons
    variants = discovered.variants
    icon_set_map = discovered.icon_sets

    if subset:
        icons = {name: path for name, path in icons.items() if name in subset}
        variants = {name: v for name, v in variants.items() if name in subset}

    prefix = icon_settings.prefix
    mode = icon_settings.mode

    has_mono = any(not icon_set_map[n].color for n in icons)
    has_color = any(icon_set_map[n].color for n in icons)

    lines: list[str] = []
    if has_mono:
        lines.append(_mono_base_rule(prefix, icon_settings.size))
    if has_color:
        lines.append(_color_base_rule(prefix, icon_settings.size))

    lines.extend(
        _icon_rule(prefix, icon_name, icons[icon_name], discovered.relatives[icon_name], mode)
        for icon_name in sorted(icons)
    )

    for icon_name in sorted(variants):
        variant_rules = _size_variant_rules(
            prefix,
            icon_name,
            variants[icon_name],
            discovered.variant_relatives[icon_name],
            mode,
        )
        if variant_rules:
            lines.append(variant_rules)

    return "\n".join(lines) + "\n"


def _mono_base_rule(prefix: str, size: str) -> str:
    return f""".{prefix} {{
  display: inline-block;
  width: {size};
  height: {size};
  vertical-align: -0.125em;
  line-height: 1;
  background-color: currentColor;
  mask-image: var(--icon-url);
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  mask-mode: alpha;
}}"""


def _color_base_rule(prefix: str, size: str) -> str:
    return f"""
.{prefix}-color {{
  display: inline-block;
  width: {size};
  height: {size};
  vertical-align: -0.125em;
  line-height: 1;
  background-image: var(--icon-url);
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}}"""


def _icon_rule(prefix: str, icon_name: str, svg_path: Path, relative: str, mode: str) -> str:
    url = _svg_url(svg_path, relative, mode)
    return f'\n.{prefix}-{icon_name} {{ --icon-url: url("{url}"); }}'


def _svg_url(svg_path: Path, relative: str, mode: str) -> str:
    if mode == "data_uri":
        svg_content = svg_path.read_text(encoding="utf-8")
        return svg_to_data_uri(svg_content)
    # mode == "url" (validated by IconxSettings.__post_init__)
    static_url = getattr(settings, "STATIC_URL", None) or "/static/"
    return f"{static_url}{relative}"


def _nearest_variant(available_sizes: list[int], target_px: int) -> int:
    """Pick the available icon size closest to the target pixel size."""
    return min(available_sizes, key=lambda s: abs(s - target_px))


def _size_variant_rules(
    prefix: str,
    icon_name: str,
    size_map: dict[int, Path],
    size_relatives: dict[int, str],
    mode: str,
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

    rules: list[str] = []
    for size_px, text_classes in sorted(variant_to_classes.items()):
        url = _svg_url(size_map[size_px], size_relatives[size_px], mode)
        selectors = ",\n".join(f".{tc}.{prefix}-{icon_name}" for tc in text_classes)
        rules.append(f"""\n{selectors} {{
  --icon-url: url("{url}");
}}""")

    return "\n".join(rules)
