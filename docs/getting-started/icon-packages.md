# Using Icon Packages

django-iconx works with any SVG icons. Install a package (npm, pip, or manual download), point your config at the SVG directory, and generate.

## Setup

Install your icon packages and symlink or copy them into your static directory:

```console
npm install lucide-static heroicons
mkdir -p static/icons
ln -s ../../node_modules/lucide-static/icons static/icons/lucide
ln -s ../../node_modules/heroicons/24/outline static/icons/heroicons
```

Configure your icon sets in Django settings:

```python
STATICFILES_DIRS = [BASE_DIR / "static"]

ICONX = {
    "sets": [
        {"path": "icons/lucide/"},
        {"path": "icons/heroicons/", "prefix": "hero"},
        {"path": "icons/custom/", "prefix": "custom", "color": "original"},
    ],
}
```

Generate the CSS:

```console
python manage.py iconx_generate
```

Use one set or many, just add or remove entries from the list. Use `"prefix"` to namespace sets and avoid name collisions. Use `"color": "original"` for multi-color SVGs that should preserve their fill colors.

The source doesn't matter: npm packages, downloaded zips, your own SVGs. The only requirement is that the directory is reachable from `STATICFILES_DIRS`.

## Pre-commit hook

To keep the generated CSS in sync, add `iconx_generate` as a pre-commit hook:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: iconx-generate
      name: iconx-generate
      entry: python manage.py iconx_generate
      language: system
      pass_filenames: false
      files: \.svg$
```

This re-generates the CSS whenever SVG files change.
