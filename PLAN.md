# django-iconx Plan

CSS-only icon system for Django. Generate a CSS file from SVG sources, use icons via plain HTML classes.

## Core Concept

```html
<!-- preferred: plain HTML + CSS classes -->
<i class="icon icon-search"></i>
<span class="icon icon-chevron-down"></span>

<!-- composes with DaisyUI buttons -->
<button class="btn btn-primary icon icon-search">Search</button>

<!-- also available: template tag -->
{% load iconx %}
{% icon "search" %}
```

Plain HTML + classes is better — no template rendering cost, works in any context (JS, HTMX responses, static HTML), composable with any CSS framework.

## Generated CSS

```css
/* base rule */
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

/* per-icon (data-URI mode) */
.icon-search::before {
  mask-image: url("data:image/svg+xml,%3Csvg...");
}

/* per-icon (URL mode) */
.icon-search::before {
  mask-image: url("/static/icons/search.svg");
}
```

Uses `::before` pseudo-element so icons compose with text content in buttons, badges, etc.
Uses `currentColor` via `background` so icons inherit text color.
Uses `1em` sizing so icons scale with font size.

## What to Build

### 1. SVG Source Registration

```python
ICONX = {
    # named icon sets — each maps a prefix to a directory of SVGs
    "sets": {
        "": "icons/",                    # default (no prefix) — icon-search
        "hero": "heroicons/outline/",    # prefixed — icon-hero-arrow-left
    },
    "output": "static/iconx/icons.css",
    "mode": "data_uri",                  # or "url"
    "prefix": "icon",
    "size": "1em",
}
```

Each SVG file becomes an icon class: `icons/search.svg` → `.icon-search`.
See #4 for namespacing details.

### 2. CSS Code Generation

```bash
python manage.py iconx_generate
python manage.py iconx_generate --output static/iconx.css
python manage.py iconx_generate --mode url
python manage.py iconx_generate --subset search,x,eye
python manage.py iconx_generate --dry-run
```

SVGs are inlined as data URIs by default (URL-encoded, not base64). URL mode is opt-in.
See #2 for the data-URI vs URL decision.

Basic SVG normalization built-in (strip metadata, normalize colors for mask-image).
See #3 for normalization details.

### 3. Template Tag (Optional Convenience)

```python
{% load iconx %}
{% icon "search" %}                    {# → <i class="icon icon-search" aria-hidden="true"></i> #}
{% icon "search" class="text-lg" %}    {# → <i class="icon icon-search text-lg" aria-hidden="true"></i> #}
{% icon "warning" aria_label="Warning" %}  {# → <i class="icon icon-warning" role="img" aria-label="Warning"></i> #}
```

Simple wrapper — renders the `<i>` tag with automatic `aria-hidden`.
See #8 for template tag design.

### 4. Tree-Shaking Compatibility

Two strategies:
- **PurgeCSS/Tailwind** (default): generate all icons, let CSS scanning strip unused classes
- **`--subset` flag**: explicitly list icons to include

See #7 for details.

## Open Design Decisions

- #2 — Data-URI vs external URL mode
- #3 — SVG normalization approach
- #4 — Folder namespacing and prefix resolution
- #5 — Size-specific icon matching (pick best SVG variant per size)
- #6 — `::before` pseudo-element vs direct element styling
- #7 — Tree-shaking strategy
- #8 — Template tag API
- #9 — Core management command implementation
- #10 — Lucide integration approach (bundle vs document workflow)

## Not In Scope

- Icon fonts
- JavaScript runtime
- Sprite sheets
- Runtime SVG inlining
