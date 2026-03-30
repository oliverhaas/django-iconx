from __future__ import annotations

from pathlib import Path

from django_iconx.conf import IconxSettings
from django_iconx.css import generate_css

FIXTURES = Path(__file__).parent / "fixtures"


class TestGenerateCss:
    def _settings(self, **kwargs):
        defaults = {"sets": {"": str(FIXTURES / "icons")}}
        defaults.update(kwargs)
        return IconxSettings(**defaults)

    def test_base_rule_present(self):
        css = generate_css(self._settings())
        assert ".icon::before {" in css
        assert "mask-size: contain;" in css
        assert "background: currentColor;" in css

    def test_icon_rules_generated(self):
        css = generate_css(self._settings())
        assert ".icon-search::before {" in css
        assert ".icon-x::before {" in css
        assert "mask-image: url(" in css

    def test_data_uri_mode(self):
        css = generate_css(self._settings(mode="data_uri"))
        assert "data:image/svg+xml," in css

    def test_url_mode(self):
        css = generate_css(self._settings(mode="url"))
        assert "data:image/svg+xml," not in css
        assert 'mask-image: url("search.svg")' in css

    def test_custom_prefix(self):
        css = generate_css(self._settings(prefix="i"))
        assert ".i::before {" in css
        assert ".i-search::before {" in css

    def test_custom_size(self):
        css = generate_css(self._settings(size="1.5rem"))
        assert "width: 1.5rem;" in css
        assert "height: 1.5rem;" in css

    def test_subset_filter(self):
        css = generate_css(self._settings(), subset={"search"})
        assert ".icon-search::before {" in css
        assert ".icon-x::before {" not in css

    def test_ends_with_newline(self):
        css = generate_css(self._settings())
        assert css.endswith("\n")


class TestSizeVariantCss:
    def _settings(self, **kwargs):
        defaults = {"sets": {"": str(FIXTURES / "sized")}}
        defaults.update(kwargs)
        return IconxSettings(**defaults)

    def test_default_rule_uses_largest_variant(self):
        css = generate_css(self._settings())
        assert ".icon-search::before {" in css
        # The default rule should use 24px SVG (viewBox 0 0 24 24)
        assert "0%200%2024%2024" in css.split(".text-")[0]

    def test_text_xs_maps_to_smallest(self):
        css = generate_css(self._settings())
        # text-xs (12px) should map to 16px variant (nearest)
        assert ".text-xs.icon-search::before" in css

    def test_text_xl_maps_to_20(self):
        css = generate_css(self._settings())
        # text-xl (20px) should map to 20px variant
        assert ".text-xl.icon-search::before" in css

    def test_text_2xl_not_overridden(self):
        css = generate_css(self._settings())
        # text-2xl (24px) maps to 24px variant which is the default — no override needed
        assert ".text-2xl.icon-search::before" not in css

    def test_text_classes_grouped(self):
        css = generate_css(self._settings())
        # text-sm (14px) and text-base (16px) both map to 16px variant
        # They should share a rule
        assert ".text-sm.icon-search::before,\n.text-base.icon-search::before" in css

    def test_flat_set_no_variant_rules(self):
        flat_settings = IconxSettings(sets={"": str(FIXTURES / "icons")})
        css = generate_css(flat_settings)
        assert ".text-" not in css

    def test_subset_filters_variants(self):
        css = generate_css(self._settings(), subset={"search"})
        assert ".text-xs.icon-search::before" in css
        assert ".text-xs.icon-x::before" not in css
