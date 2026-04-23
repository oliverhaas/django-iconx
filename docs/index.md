# django-iconx

CSS-only icon system for Django.

Generates a single CSS file from SVG icon sources. No JavaScript or icon fonts needed. Built-in support for Lucide, Heroicons, Tabler, Phosphor, Bootstrap Icons, and Remix.

```html
<i class="icon icon-search"></i>
<i class="icon icon-check text-2xl text-green-500"></i>
<i class="icon-color icon-logo"></i>
```

Icons set a `--icon-url` CSS variable. The `.icon` base class renders it via `mask-image` with `currentColor`, so icons inherit text color and scale with font size via Tailwind `text-*` classes. The `.icon-color` base class renders the same variable via `background-image`, preserving the SVG's original colors — use it for logos and other multi-color artwork.

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
```

```console
python manage.py iconx add lucide
```

That downloads the icons and generates the CSS. Include it in your template or Tailwind entry point:

```css
@import "tailwindcss";
@import "./static/iconx/icons.css";
```

See [Installation](getting-started/installation.md) for the full setup guide.
