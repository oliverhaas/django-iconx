from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IconPackage:
    repo: str
    svg_path: str
    styles: tuple[str, ...] = ()


REGISTRY: dict[str, IconPackage] = {
    "lucide": IconPackage(
        repo="lucide-icons/lucide",
        svg_path="icons/",
    ),
    "heroicons": IconPackage(
        repo="tailwindlabs/heroicons",
        svg_path="optimized/",
        styles=("16", "20", "24"),
    ),
    "tabler": IconPackage(
        repo="tabler/tabler-icons",
        svg_path="icons/",
        styles=("outline", "filled"),
    ),
    "phosphor": IconPackage(
        repo="phosphor-icons/core",
        svg_path="assets/",
        styles=("thin", "light", "regular", "bold", "fill", "duotone"),
    ),
    "bootstrap": IconPackage(
        repo="twbs/icons",
        svg_path="icons/",
    ),
    "remix": IconPackage(
        repo="Remix-Design/RemixIcon",
        svg_path="icons/",
    ),
}
