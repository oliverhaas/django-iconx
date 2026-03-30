from __future__ import annotations

from pathlib import Path

from django_iconx.conf import IconxSettings
from django_iconx.svg import discover_svg_variants, discover_svgs, normalize_svg, svg_to_data_uri

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

    def test_replaces_currentcolor_with_black(self):
        svg = '<svg fill="currentColor" stroke="currentColor"><path/></svg>'
        result = normalize_svg(svg)
        assert 'fill="black"' in result
        assert 'stroke="black"' in result
        assert "currentColor" not in result

    def test_preserves_fill_none(self):
        svg = '<svg fill="none"><path/></svg>'
        result = normalize_svg(svg)
        assert 'fill="none"' in result

    def test_removes_decorative_fills(self):
        svg = '<svg fill="#ff0000"><path/></svg>'
        result = normalize_svg(svg)
        assert "#ff0000" not in result

    def test_preserves_stroke_attributes(self):
        svg = '<svg stroke="black" stroke-width="2"><path/></svg>'
        result = normalize_svg(svg)
        assert 'stroke="black"' in result
        assert 'stroke-width="2"' in result

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
        assert "%3Csvg" in uri  # URL-encoded <svg

    def test_not_base64(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><path/></svg>'
        uri = svg_to_data_uri(svg)
        assert "base64" not in uri


class TestDiscoverSvgs:
    def test_discovers_icons_from_directory(self):
        settings = IconxSettings(sets={"": str(FIXTURES / "icons")})
        icons = discover_svgs(settings)
        assert "search" in icons
        assert "x" in icons
        assert icons["search"].name == "search.svg"

    def test_prefixed_set(self):
        settings = IconxSettings(sets={"hero": str(FIXTURES / "heroicons")})
        icons = discover_svgs(settings)
        assert "hero-arrow-left" in icons

    def test_multiple_sets(self):
        settings = IconxSettings(
            sets={
                "": str(FIXTURES / "icons"),
                "hero": str(FIXTURES / "heroicons"),
            }
        )
        icons = discover_svgs(settings)
        assert "search" in icons
        assert "hero-arrow-left" in icons

    def test_nonexistent_directory_skipped(self):
        settings = IconxSettings(sets={"": "/nonexistent/path"})
        icons = discover_svgs(settings)
        assert icons == {}

    def test_size_dirs_uses_largest_as_default(self):
        settings = IconxSettings(sets={"": str(FIXTURES / "sized")})
        icons = discover_svgs(settings)
        assert "search" in icons
        # Default should be the 24px variant (largest)
        assert "24" in str(icons["search"])

    def test_size_dirs_icon_names_exclude_size_prefix(self):
        settings = IconxSettings(sets={"": str(FIXTURES / "sized")})
        icons = discover_svgs(settings)
        # Should be "search", not "24-search"
        assert "search" in icons
        assert "x" in icons
        assert "16-search" not in icons
        assert "24-search" not in icons


class TestDiscoverSvgVariants:
    def test_discovers_variants(self):
        settings = IconxSettings(sets={"": str(FIXTURES / "sized")})
        variants = discover_svg_variants(settings)
        assert "search" in variants
        assert sorted(variants["search"].keys()) == [16, 20, 24]

    def test_x_has_two_variants(self):
        settings = IconxSettings(sets={"": str(FIXTURES / "sized")})
        variants = discover_svg_variants(settings)
        assert "x" in variants
        assert sorted(variants["x"].keys()) == [16, 24]

    def test_flat_set_has_no_variants(self):
        settings = IconxSettings(sets={"": str(FIXTURES / "icons")})
        variants = discover_svg_variants(settings)
        assert variants == {}

    def test_prefixed_set_variants(self):
        settings = IconxSettings(sets={"hero": str(FIXTURES / "sized")})
        variants = discover_svg_variants(settings)
        assert "hero-search" in variants
        assert sorted(variants["hero-search"].keys()) == [16, 20, 24]
