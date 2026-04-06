# Installation

```console
uv add django-iconx
```

Add `django_iconx` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_iconx",
]
```

Place your SVG icons in a directory reachable from `STATICFILES_DIRS` and configure the icon sets:

```python
STATICFILES_DIRS = [BASE_DIR / "static"]

ICONX = {
    "sets": ["icons/"],
}
```

Generate the CSS file:

```console
python manage.py iconx_generate
```

Include the generated CSS in your templates (or Tailwind entry point) and use icons via CSS classes:

```html
<i class="icon icon-search" aria-hidden="true"></i>
```

See [Icon Packages](icon-packages.md) for using Lucide, Heroicons, and other icon sets. See [Configuration](../reference/configuration.md) for all available settings.
