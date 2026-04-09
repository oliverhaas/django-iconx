# Installation

```console
uv add django-iconx
```

Add `django_iconx` to your `INSTALLED_APPS` and configure `STATICFILES_DIRS`:

```python
INSTALLED_APPS = [
    # ...
    "django_iconx",
]

STATICFILES_DIRS = [BASE_DIR / "static"]
```

Add an icon package and generate the CSS:

```console
python manage.py iconx add lucide
```

This downloads Lucide icons to `static/icons/lucide/` and generates `static/iconx/icons.css`. Include the CSS in your templates or Tailwind entry point:

```html
<i class="icon icon-lucide-search"></i>
```

See [Icon Packages](icon-packages.md) for other icon sets and custom SVGs. See [Configuration](../reference/configuration.md) for all available settings.
