# Icon Packages

django-iconx can download icon packages directly from GitHub. No npm required.

## Built-in packages

| Package | Command | Icons |
|---------|---------|-------|
| [Lucide](https://lucide.dev) | `iconx add lucide` | ~1,300 |
| [Heroicons](https://heroicons.com) | `iconx add heroicons` | ~460 |
| [Tabler](https://tabler.io/icons) | `iconx add tabler` | ~6,000 |
| [Phosphor](https://phosphoricons.com) | `iconx add phosphor` | ~7,000 |
| [Bootstrap](https://icons.getbootstrap.com) | `iconx add bootstrap` | ~2,000 |

```console
python manage.py iconx add lucide
```

This downloads the SVGs to `static/icons/lucide/` and generates the CSS. Icons are available as `icon-lucide-search`, `icon-lucide-arrow-left`, etc.

## Styles

Some packages organize icons into styles (outline/filled, sizes, weights). Use a slash to pick a specific style:

```console
python manage.py iconx add heroicons/24
python manage.py iconx add tabler/outline
python manage.py iconx add phosphor/regular
```

Without a style, all variants are downloaded.

## Multiple packages

Add as many packages as you need. Each gets its own subdirectory under `static/icons/`, so names stay namespaced:

```console
python manage.py iconx add lucide
python manage.py iconx add heroicons/24
```

## Pinning versions

By default, the latest release is downloaded. Pin a version with `--version`:

```console
python manage.py iconx add lucide --version v1.7.0
```

## Custom SVGs

For your own SVGs, place them in a directory under `STATICFILES_DIRS` and configure the set in your Django settings:

```python
ICONX = {
    "sets": [
        "icons/",
        {"path": "logos/", "color": "original"},
    ],
}
```

Then regenerate:

```console
python manage.py iconx generate
```

Use `"color": "original"` for multi-color SVGs that should preserve their fill colors.

## Pre-commit hook

To keep the generated CSS in sync when SVG files change:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: iconx-generate
      name: iconx-generate
      entry: python manage.py iconx generate
      language: system
      pass_filenames: false
      files: \.svg$
```
