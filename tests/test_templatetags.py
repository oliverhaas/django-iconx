from __future__ import annotations

from django.template import Context, Template
from django.test import override_settings


class TestIconTag:
    def _render(self, template_string, context=None):
        t = Template(template_string)
        return t.render(Context(context or {}))

    def test_basic_icon(self):
        html = self._render('{% load iconx %}{% icon "search" %}')
        assert 'class="icon icon-search"' in html
        assert 'aria-hidden="true"' in html
        assert "<i " in html

    def test_extra_class(self):
        html = self._render('{% load iconx %}{% icon "search" class="text-lg" %}')
        assert "icon icon-search text-lg" in html

    def test_aria_label(self):
        html = self._render('{% load iconx %}{% icon "warning" aria_label="Warning" %}')
        assert 'aria-label="Warning"' in html
        assert 'role="img"' in html
        assert "aria-hidden" not in html

    def test_data_attributes(self):
        html = self._render('{% load iconx %}{% icon "search" data_controller="icon" data_value="1" %}')
        assert 'data-controller="icon"' in html
        assert 'data-value="1"' in html

    def test_escapes_attribute_values(self):
        html = self._render('{% load iconx %}{% icon "search" data_val="<script>" %}')
        assert "&lt;script&gt;" in html
        assert "<script>" not in html

    @override_settings(ICONX={"prefix": "icn"})
    def test_custom_prefix(self):
        html = self._render('{% load iconx %}{% icon "search" %}')
        assert 'class="icn icn-search"' in html
