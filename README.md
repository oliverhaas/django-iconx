# django-iconx

[![PyPI version](https://img.shields.io/pypi/v/django-iconx.svg?style=flat)](https://pypi.org/project/django-iconx/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-iconx.svg)](https://pypi.org/project/django-iconx/)
[![CI](https://github.com/oliverhaas/django-iconx/actions/workflows/ci.yml/badge.svg)](https://github.com/oliverhaas/django-iconx/actions/workflows/ci.yml)

CSS-only icon system for Django.

![django-iconx demo](docs/assets/demo.png)

Generates a single CSS file from SVG icon sources. No JavaScript, no icon fonts.

```console
python manage.py iconx add lucide
```

```html
<i class="icon icon-lucide-search"></i>
<span class="icon icon-lucide-check text-2xl text-green-500"></span>
```

Built-in support for Lucide, Heroicons, Tabler, Phosphor, Bootstrap Icons, and Remix. Or bring your own SVGs.

## How it works and what the upsides are

Mono icons use `mask-image` with `background-color: currentColor`, so the SVG acts as a mask and the icon inherits text color. Multi-color icons use `background-image` to preserve original SVG colors.

The output is plain CSS classes: no runtime, no bundler plugin, no framework coupling. The approach is not Django-specific; Django is just a good fit because its static file conventions make wiring it up easy. Any stack that serves CSS and renders HTML can use the generated stylesheet directly.

```css
.icon { display: inline-block; width: 1em; height: 1em; }

.icon-search, .icon-check { background-color: currentColor; mask-size: contain; mask-mode: alpha; }
.icon-search { mask-image: url("/static/icons/search.svg"); }

.icon-logo { background-image: url("/static/logos/logo.svg"); }
```

- `currentColor` + `mask-image`: icons inherit text color
- `1em` sizing: icons scale with font size / Tailwind `text-*`
- Direct element styling, no `::before` pseudo-element
- Tree-shakeable: PurgeCSS strips unused `.icon-*` rules

## Browser support

CSS `mask-image` is supported unprefixed in all modern browsers since Dec 2023 (~97% global coverage). Tailwind v4 handles vendor prefixing automatically:

```css
@import "tailwindcss";
@import "./static/iconx/icons.css";
```

## Quick start

```console
uv add django-iconx
```

```python
INSTALLED_APPS = ["django_iconx", ...]
STATICFILES_DIRS = [BASE_DIR / "static"]
```

```console
python manage.py iconx add lucide
```

That downloads Lucide icons and generates the CSS. Include the CSS in your template or Tailwind entry point and use icons via class names. See the full documentation at [oliverhaas.github.io/django-iconx](https://oliverhaas.github.io/django-iconx/) for custom SVGs, multiple icon sets, and configuration options.

## License

MIT
