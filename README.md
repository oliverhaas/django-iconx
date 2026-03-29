# django-iconx

[![PyPI version](https://img.shields.io/pypi/v/django-iconx.svg?style=flat)](https://pypi.org/project/django-iconx/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-iconx.svg)](https://pypi.org/project/django-iconx/)
[![CI](https://github.com/oliverhaas/django-iconx/actions/workflows/ci.yml/badge.svg)](https://github.com/oliverhaas/django-iconx/actions/workflows/ci.yml)

CSS-only icon system for Django.

Generates a single CSS file from SVG icon sources (e.g. Lucide, Heroicons, or your own SVGs). Icons are rendered purely via CSS — no JavaScript, no icon fonts, no template tags needed.

## Usage

```html
<!-- standalone icon -->
<i class="icon icon-search"></i>

<!-- composes naturally with daisyUI buttons (or any flexbox container) -->
<button class="btn btn-primary icon icon-search">Search</button>

<!-- icon-only button -->
<button class="btn btn-primary btn-square icon icon-search"></button>
```

## How it works

Each icon becomes a CSS class using `mask-image` on a `::before` pseudo-element:

```css
.icon::before {
  display: inline-block;
  width: 1em;
  height: 1em;
  content: "";
  background: currentColor;
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
}

.icon-search::before {
  mask-image: url("data:image/svg+xml,...");
}
```

Key design choices:
- **`currentColor`** — icons inherit text color automatically
- **`1em` sizing** — icons scale with font size
- **`::before` pseudo-element** — participates in flexbox layout, composes with buttons/badges/etc.
- **Data URIs** — no external requests, everything in one CSS file
- **Tree-shakeable** — only the icons you use end up in the output (via Tailwind/PurgeCSS scanning)

## Installation

```console
pip install django-iconx
```

## Documentation

Full documentation at [oliverhaas.github.io/django-iconx](https://oliverhaas.github.io/django-iconx/)

## License

MIT
