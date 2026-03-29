# django-iconx Plan

CSS-only icon system for Django. Generate a CSS file from SVG sources, use icons via plain HTML classes.

## Core Concept

```html
<!-- preferred: plain HTML + CSS classes -->
<i class="icon icon-search"></i>
<button class="btn btn-primary icon icon-search">Search</button>

<!-- also available: template tag -->
{% load iconx %}
{% icon "search" %}
```

Plain HTML + classes is better — no template rendering cost, works in any context (JS, HTMX responses, static HTML), composable with any CSS framework.

## What to Build

### 1. SVG Source Registration

Straightforward way to include icon SVGs. Configure in settings:

```python
ICONX = {
    # named icon sets — each maps a prefix to a directory of SVGs
    "sets": {
        "": "icons/",                    # default (no prefix) — icon-search
        "hero": "heroicons/outline/",    # prefixed — icon-hero-arrow-left
    },
}
```

Each SVG file becomes an icon class: `icons/search.svg` → `.icon-search`.

### 2. CSS Code Generation

Management command that reads SVGs and produces a single CSS file:

```bash
python manage.py iconx_generate --output static/iconx.css
```

Output:

```css
/* base */
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

/* per-icon */
.icon-search::before {
  mask-image: url("data:image/svg+xml,...");
}
```

SVGs are inlined as data URIs (URL-encoded, not base64 — smaller for simple SVGs). Strip unnecessary attributes (fill, stroke colors) so currentColor works.

### 3. Template Tag (Optional Convenience)

```python
{% load iconx %}
{% icon "search" %}                    {# → <i class="icon icon-search"></i> #}
{% icon "search" class="text-lg" %}    {# → <i class="icon icon-search text-lg"></i> #}
```

Simple wrapper — just renders the `<i>` tag. No special logic.

### 4. Tree-Shaking Compatibility

The generated CSS contains all icons. When used with Tailwind/PurgeCSS, only icons whose classes appear in templates are kept. No special integration needed — just works because classes are in the HTML.

## Not In Scope

- Icon fonts
- JavaScript runtime
- Sprite sheets
- Runtime SVG inlining
