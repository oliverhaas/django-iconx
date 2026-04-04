from __future__ import annotations

from pathlib import Path

from django_iconx.conf import IconSet, IconxSettings
from django_iconx.css import generate_css

FIXTURES = Path(__file__).parent / "fixtures"


class TestGenerateCss:
    def _settings(self, **kwargs):
        defaults = {"sets": [IconSet("icons/")]}
        defaults.update(kwargs)
        return IconxSettings(**defaults)

    def test_base_rule_present(self):
        css = generate_css(self._settings())
        assert ".icon {" in css
        assert "vertical-align: -0.125em;" in css
        assert "line-height: 1;" in css

    def test_mono_base_rule(self):
        css = generate_css(self._settings())
        assert "background-color: currentColor;" in css
        assert "mask-mode: alpha;" in css
        assert "mask-size: contain;" in css

    def test_no_before_pseudo(self):
        css = generate_css(self._settings())
        assert "::before" not in css

    def test_icon_rules_generated(self):
        css = generate_css(self._settings())
        assert ".icon-search {" in css
        assert ".icon-x {" in css
        assert "mask-image: url(" in css

    def test_data_uri_mode(self):
        css = generate_css(self._settings(mode="data_uri"))
        assert "data:image/svg+xml," in css

    def test_url_mode(self):
        css = generate_css(self._settings(mode="url"))
        assert "data:image/svg+xml," not in css
        assert 'mask-image: url("/static/icons/search.svg")' in css

    def test_custom_prefix(self):
        css = generate_css(self._settings(prefix="i"))
        assert ".i {" in css
        assert ".i-search {" in css

    def test_custom_size(self):
        css = generate_css(self._settings(size="1.5rem"))
        assert "width: 1.5rem;" in css
        assert "height: 1.5rem;" in css

    def test_subset_filter(self):
        css = generate_css(self._settings(), subset={"search"})
        assert ".icon-search {" in css
        assert ".icon-x" not in css.replace(".icon {", "")

    def test_ends_with_newline(self):
        css = generate_css(self._settings())
        assert css.endswith("\n")


class TestSizeVariantCss:
    def _settings(self, **kwargs):
        defaults = {"sets": [IconSet("sized/")]}
        defaults.update(kwargs)
        return IconxSettings(**defaults)

    def test_default_rule_uses_largest_variant(self):
        css = generate_css(self._settings(mode="data_uri"))
        assert ".icon-search {" in css
        # The default rule should use 24px SVG (viewBox 0 0 24 24)
        assert "0%200%2024%2024" in css.split(".text-")[0]

    def test_text_xs_maps_to_smallest(self):
        css = generate_css(self._settings())
        assert ".text-xs.icon-search" in css

    def test_text_xl_maps_to_20(self):
        css = generate_css(self._settings())
        assert ".text-xl.icon-search" in css

    def test_text_2xl_not_overridden(self):
        css = generate_css(self._settings())
        assert ".text-2xl.icon-search" not in css

    def test_text_classes_grouped(self):
        css = generate_css(self._settings())
        assert ".text-sm.icon-search,\n.text-base.icon-search" in css

    def test_flat_set_no_variant_rules(self):
        settings = IconxSettings(sets=[IconSet("icons/")])
        css = generate_css(settings)
        assert ".text-" not in css

    def test_subset_filters_variants(self):
        css = generate_css(self._settings(), subset={"search"})
        assert ".text-xs.icon-search" in css
        assert ".text-xs.icon-x" not in css


class TestOriginalColorCss:
    def _settings(self, **kwargs):
        defaults = {"sets": [IconSet("icons/", color="original")]}
        defaults.update(kwargs)
        return IconxSettings(**defaults)

    def test_uses_background_image(self):
        css = generate_css(self._settings())
        assert "background-image: url(" in css
        assert "background-size: contain;" in css

    def test_no_mask_for_original(self):
        css = generate_css(self._settings())
        assert "mask-image" not in css
        assert "mask-mode" not in css

    def test_multi_base_rule(self):
        css = generate_css(self._settings())
        assert "background-size: contain;" in css
        assert "background-repeat: no-repeat;" in css
        assert "background-position: center;" in css

    def test_mixed_sets(self):
        settings = IconxSettings(
            sets=[
                IconSet("icons/", color="mono"),
                IconSet("heroicons/", prefix="logo", color="original"),
            ],
        )
        css = generate_css(settings)
        # mono icons use mask-image
        assert ".icon-search { mask-image: url(" in css
        # original icons use background-image
        assert ".icon-logo-arrow-left { background-image: url(" in css

    def test_url_mode_original(self):
        css = generate_css(self._settings(mode="url"))
        assert 'background-image: url("/static/icons/search.svg")' in css
