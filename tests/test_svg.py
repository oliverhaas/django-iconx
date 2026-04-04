from __future__ import annotations

import logging
from pathlib import Path

import pytest

from django_iconx.conf import IconSet, IconxSettings
from django_iconx.svg import discover, discover_svg_variants, discover_svgs, normalize_svg, svg_to_data_uri

FIXTURES = Path(__file__).parent / "fixtures"


class TestNormalizeSvg:
    def test_strips_xml_declaration(self):
        svg = '<?xml version="1.0"?><svg><path d="M0 0"/></svg>'
        result = normalize_svg(svg)
        assert "<?xml" not in result
        assert "<svg>" in result

    def test_strips_comments(self):
        svg = "<!-- comment --><svg><path/></svg>"
        result = normalize_svg(svg)
        assert "comment" not in result

    def test_strips_metadata(self):
        svg = "<svg><metadata>foo</metadata><path/></svg>"
        result = normalize_svg(svg)
        assert "metadata" not in result

    def test_preserves_all_colors(self):
        svg = '<svg fill="currentColor" stroke="#ff0000"><path/></svg>'
        result = normalize_svg(svg)
        assert 'fill="currentColor"' in result
        assert 'stroke="#ff0000"' in result

    def test_collapses_whitespace(self):
        svg = "<svg>  \n  <path/>  \n  </svg>"
        result = normalize_svg(svg)
        assert "\n" not in result
        assert "  " not in result


class TestSvgToDataUri:
    def test_produces_data_uri(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>'
        uri = svg_to_data_uri(svg)
        assert uri.startswith("data:image/svg+xml,")
        assert "%3Csvg" in uri

    def test_not_base64(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'
        uri = svg_to_data_uri(svg)
        assert "base64" not in uri


class TestDiscoverSvgs:
    def test_discovers_icons_from_directory(self):
        settings = IconxSettings(sets=[IconSet("icons/")])
        icons = discover_svgs(settings)
        assert "search" in icons
        assert "x" in icons
        assert icons["search"].name == "search.svg"

    def test_prefixed_set(self):
        settings = IconxSettings(sets=[IconSet("heroicons/", prefix="hero")])
        icons = discover_svgs(settings)
        assert "hero-arrow-left" in icons

    def test_multiple_sets(self):
        settings = IconxSettings(
            sets=[
                IconSet("icons/"),
                IconSet("heroicons/", prefix="hero"),
            ],
        )
        icons = discover_svgs(settings)
        assert "search" in icons
        assert "hero-arrow-left" in icons

    def test_no_match_skipped(self):
        settings = IconxSettings(sets=[IconSet("nonexistent/")])
        icons = discover_svgs(settings)
        assert icons == {}

    def test_first_match_wins(self):
        settings = IconxSettings(
            sets=[
                IconSet("icons/", prefix="first"),
                IconSet("icons/", prefix="second"),
            ],
        )
        icons = discover_svgs(settings)
        assert "first-search" in icons
        assert "second-search" not in icons

    def test_regex_path(self):
        settings = IconxSettings(sets=[IconSet(r"icons/s.*\.svg$")])
        icons = discover_svgs(settings)
        # "icons/search.svg" matches, remainder is "" so icon name from match
        # Actually: regex matches the whole path, remainder is empty
        assert len(icons) == 1  # only search.svg matches

    def test_size_dirs_uses_largest_as_default(self):
        settings = IconxSettings(sets=[IconSet("sized/")])
        icons = discover_svgs(settings)
        assert "search" in icons
        assert "24" in str(icons["search"])

    def test_size_dirs_icon_names_exclude_size_prefix(self):
        settings = IconxSettings(sets=[IconSet("sized/")])
        icons = discover_svgs(settings)
        assert "search" in icons
        assert "x" in icons

    def test_name_collision_raises(self):
        # icons/search.svg and dupes/search.svg both produce "search" with no prefix
        settings = IconxSettings(
            sets=[
                IconSet("icons/"),
                IconSet("dupes/"),
            ],
        )
        with pytest.raises(ValueError, match=r"collision.*search"):
            discover_svgs(settings)

    def test_name_collision_skip_warns_and_keeps_first(self, caplog):
        settings = IconxSettings(
            sets=[
                IconSet("icons/"),
                IconSet("dupes/"),
            ],
        )
        with caplog.at_level(logging.WARNING, logger="django_iconx"):
            discovered = discover(settings, skip_collisions=True)
        assert "collision" in caplog.text.lower()
        assert "search" in discovered.icons


class TestDiscoverSvgVariants:
    def test_discovers_variants(self):
        settings = IconxSettings(sets=[IconSet("sized/")])
        variants = discover_svg_variants(settings)
        assert "search" in variants
        assert sorted(variants["search"].keys()) == [16, 20, 24]

    def test_x_has_two_variants(self):
        settings = IconxSettings(sets=[IconSet("sized/")])
        variants = discover_svg_variants(settings)
        assert "x" in variants
        assert sorted(variants["x"].keys()) == [16, 24]

    def test_flat_set_has_no_variants(self):
        settings = IconxSettings(sets=[IconSet("icons/")])
        variants = discover_svg_variants(settings)
        assert variants == {}

    def test_prefixed_set_variants(self):
        settings = IconxSettings(sets=[IconSet("sized/", prefix="hero")])
        variants = discover_svg_variants(settings)
        assert "hero-search" in variants
        assert sorted(variants["hero-search"].keys()) == [16, 20, 24]
