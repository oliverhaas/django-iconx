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
| [Remix](https://remixicon.com) | `iconx add remix` | ~2,800 |

```console
python manage.py iconx add lucide
```

This downloads the SVGs to `static/icons/lucide/` and generates the CSS. Icons are available as `icon-search`, `icon-arrow-left`, etc.

## Styles

Some packages organize icons into styles (outline/filled, sizes, weights). Use a slash to pick a specific style:

```console
python manage.py iconx add heroicons/24
python manage.py iconx add tabler/outline
python manage.py iconx add phosphor/regular
```

Without a style, all variants are downloaded.

## Multiple packages

Add as many packages as you need. Each gets its own subdirectory under `static/icons/`:

```console
python manage.py iconx add lucide
python manage.py iconx add heroicons/24
```

By default, class names use filenames only (e.g. `icon-search`). If two packages contain icons with the same filename, `iconx generate` will report a collision. Use `include_path` or `prefix` to disambiguate:

```python
ICONX = {
    "sets": [
        {"path": "icons/lucide/", "prefix": "lucide"},
        {"path": "icons/heroicons/", "prefix": "hero"},
    ],
}
```

This produces `.icon-lucide-search` and `.icon-hero-search`. See [Configuration](../reference/configuration.md) for all options.

## Pinning versions

By default, the latest release is downloaded. Pin a version with `--version`:

```console
python manage.py iconx add lucide --version v1.7.0
```

## GitHub rate limits

The `add` command uses the GitHub API to find the latest release. Unauthenticated requests are limited to 60/hour, which can cause 403 errors.

Two ways to avoid this:

- **Pin a version** with `--version` to skip the API call entirely
- **Set `GITHUB_TOKEN`** to raise the limit to 5,000/hour:
  ```console
  export GITHUB_TOKEN=ghp_...
  python manage.py iconx add lucide
  ```

## Custom SVGs

For your own SVGs, place them in a directory under `STATICFILES_DIRS` and configure the set in your Django settings:

```python
ICONX = {
    "sets": [
        "icons/",
        {"path": "logos/", "color": True},
    ],
}
```

Then regenerate:

```console
python manage.py iconx generate
```

Use `"color": True` for multi-color SVGs that should preserve their fill colors. In HTML, render these with the `.icon-color` base class instead of `.icon`:

```html
<i class="icon icon-search"></i>        <!-- monochrome, inherits text color -->
<i class="icon-color icon-logo"></i>    <!-- keeps original SVG colors -->
```

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
