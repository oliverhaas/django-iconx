from __future__ import annotations

from django import template
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from django_iconx.conf import get_settings

register = template.Library()


@register.simple_tag
def icon(name: str, **kwargs: str) -> str:
    """Render an icon element.

    Usage:
        {% load iconx %}
        {% icon "search" %}
        {% icon "search" class="text-lg" %}
        {% icon "warning" aria_label="Warning" %}
    """
    prefix = get_settings().prefix
    classes = f"{prefix} {prefix}-{name}"

    extra_class = kwargs.pop("class", "")
    if extra_class:
        classes = f"{classes} {extra_class}"

    aria_label = kwargs.pop("aria_label", "")

    # Build attribute pairs (each value is escaped individually)
    attrs_parts: list[str] = []
    if aria_label:
        attrs_parts.append(f'role="img" aria-label="{escape(aria_label)}"')
    else:
        attrs_parts.append('aria-hidden="true"')

    for key, value in sorted(kwargs.items()):
        attr_name = key.replace("_", "-")
        attrs_parts.append(f'{attr_name}="{escape(value)}"')

    attrs = mark_safe(" ".join(attrs_parts))  # noqa: S308
    return format_html('<i class="{}" {}></i>', classes, attrs)
