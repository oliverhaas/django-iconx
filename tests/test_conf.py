from __future__ import annotations

import pytest
from django.test import override_settings

from django_iconx.conf import IconxSettings, get_settings


class TestIconxSettings:
    def test_defaults(self):
        s = IconxSettings()
        assert s.sets == {"": "icons/"}
        assert s.output == "static/iconx/icons.css"
        assert s.mode == "data_uri"
        assert s.prefix == "icon"
        assert s.size == "1em"

    def test_custom_values(self):
        s = IconxSettings(
            sets={"hero": "heroicons/"},
            output="out.css",
            mode="url",
            prefix="i",
            size="1.5em",
        )
        assert s.sets == {"hero": "heroicons/"}
        assert s.mode == "url"

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="Invalid mode"):
            IconxSettings(mode="inline")

    @override_settings(ICONX={"prefix": "icn", "mode": "url"})
    def test_get_settings_from_django(self):
        s = get_settings()
        assert s.prefix == "icn"
        assert s.mode == "url"
        # defaults still apply for unset keys
        assert s.size == "1em"

    def test_get_settings_defaults(self):
        s = get_settings()
        assert s.prefix == "icon"
