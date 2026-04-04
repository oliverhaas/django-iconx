from __future__ import annotations

import pytest
from django.test import override_settings

from django_iconx.conf import IconSet, IconxSettings, get_settings


class TestIconSet:
    def test_defaults(self):
        s = IconSet(path="icons/")
        assert s.prefix == ""
        assert s.color == "mono"

    def test_original_color(self):
        s = IconSet(path="logos/", color="original")
        assert s.color == "original"

    def test_custom_prefix(self):
        s = IconSet(path="heroicons/", prefix="hero")
        assert s.prefix == "hero"

    def test_invalid_color(self):
        with pytest.raises(ValueError, match="Invalid color"):
            IconSet(path="icons/", color="rainbow")


class TestIconxSettings:
    def test_defaults(self):
        s = IconxSettings()
        assert s.sets == [IconSet("icons/")]
        assert s.output == "static/iconx/icons.css"
        assert s.mode == "url"
        assert s.prefix == "icon"
        assert s.size == "1em"

    def test_custom_values(self):
        s = IconxSettings(
            sets=[IconSet("heroicons/", prefix="hero")],
            output="out.css",
            mode="url",
            prefix="i",
            size="1.5em",
        )
        assert s.sets[0].prefix == "hero"
        assert s.mode == "url"

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="Invalid mode"):
            IconxSettings(mode="inline")

    @override_settings(ICONX={"prefix": "icn", "mode": "url"})
    def test_get_settings_from_django(self):
        s = get_settings()
        assert s.prefix == "icn"
        assert s.mode == "url"
        assert s.size == "1em"

    def test_get_settings_defaults(self):
        s = get_settings()
        assert s.prefix == "icon"

    @override_settings(
        ICONX={
            "sets": [
                "icons/",
                {"path": "logos/", "prefix": "logo", "color": "original"},
            ],
        },
    )
    def test_get_settings_normalizes_sets(self):
        s = get_settings()
        assert s.sets[0] == IconSet("icons/")
        assert s.sets[1] == IconSet("logos/", prefix="logo", color="original")
