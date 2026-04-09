# Configuration

All settings live under the `ICONX` dict in your Django settings module.

```python
ICONX = {
    "sets": ["icons/"],
    "output": "static/iconx/icons.css",
    "mode": "url",
    "prefix": "icon",
    "size": "1em",
}
```

## Settings

### `sets`

List of icon set definitions. Each entry is either a path string or a dict with options.

**Default:** `["icons/"]`

```python
ICONX = {
    "sets": [
        "icons/",                                          # string shorthand
        {"path": "heroicons/", "prefix": "hero"},          # with prefix
        {"path": "logos/", "color": "original"},            # multi-color
    ],
}
```

Paths are matched as regex patterns against file paths relative to `STATICFILES_DIRS`. A simple string like `"icons/"` matches any file under an `icons/` directory.

#### Icon set options

| Option | Default | Description |
|--------|---------|-------------|
| `path` | (required) | Regex pattern to match against relative file paths |
| `prefix` | `""` | Prefix added to icon class names (e.g. `prefix="hero"` produces `.icon-hero-search`) |
| `color` | `"mono"` | `"mono"` for single-color icons (uses CSS mask), `"original"` for multi-color (uses background-image) |
| `include_path` | `false` | Include directory structure in class names. `false`: `icons/lucide/search.svg` produces `.icon-search`. `true`: produces `.icon-lucide-search`. |

### `output`

Path where the generated CSS file is written.

**Default:** `"static/iconx/icons.css"`

### `mode`

How SVG sources are referenced in the generated CSS.

**Default:** `"url"`

| Mode | Description |
|------|-------------|
| `"url"` | References SVGs via URL path (uses `STATIC_URL` prefix). Files must be served by your static file setup. |
| `"data_uri"` | Inlines SVGs as URL-encoded data URIs. No separate file serving needed, but increases CSS file size. |

### `prefix`

CSS class prefix for all icons.

**Default:** `"icon"`

With the default prefix, icons get classes like `.icon` (base) and `.icon-search` (per-icon).

### `size`

Default icon dimensions (width and height).

**Default:** `"1em"`

Since icons use `1em` sizing by default, they scale with font size. Use Tailwind `text-*` classes to control size.

## Management commands

### `iconx add`

```console
python manage.py iconx add <package> [options]
```

Downloads an icon package from GitHub and generates CSS.

| Argument / Flag | Description |
|------|-------------|
| `package` | Package name, e.g. `lucide`, `heroicons/24`, `tabler/outline` |
| `--version TAG` | Specific version tag (default: latest release) |
| `--no-generate` | Skip CSS generation after download |

### `iconx generate`

```console
python manage.py iconx generate [options]
```

| Flag | Description |
|------|-------------|
| `--output PATH` | Override the output file path |
| `--mode {url,data_uri}` | Override the embedding mode |
| `--subset name1,name2` | Only generate CSS for the listed icon names |
| `--dry-run` | Print CSS to stdout instead of writing to file |
| `--skip-name-collisions` | Warn on name collisions instead of aborting |
