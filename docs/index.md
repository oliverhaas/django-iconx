# django-iconx

CSS-only icon system for Django.

Generates a single CSS file from SVG icon sources (e.g. Lucide, Heroicons, or your own SVGs). Icons are rendered purely via CSS -- no JavaScript or icon fonts needed.

```html
<i class="icon icon-search" aria-hidden="true"></i>
<i class="icon icon-check text-2xl text-green-500" aria-hidden="true"></i>
```

Mono icons use `mask-image` with `currentColor`, so they inherit text color and scale with font size via Tailwind `text-*` classes. Multi-color icons use `background-image` to preserve original SVG colors.

A `{% icon %}` template tag is included for convenience but not required -- the CSS classes work standalone.

## Quick start

```console
uv add django-iconx
```

```python
INSTALLED_APPS = [
    # ...
    "django_iconx",
]

STATICFILES_DIRS = [BASE_DIR / "static"]

ICONX = {
    "sets": ["icons/"],
}
```

```console
python manage.py iconx_generate
```

See [Installation](getting-started/installation.md) for the full setup guide.
