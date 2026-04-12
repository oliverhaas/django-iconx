# Changelog

## 0.2.0

- `iconx remove <package>` command to delete downloaded icon packages
- `include_path` option for icon sets: include directory structure in class names
- Simplified default class naming: filenames only (e.g. `icon-search` instead of `icon-lucide-search`)
- Invalid regex patterns in set paths now produce clear error messages
- `iconx generate` name collision errors now exit with non-zero status

## 0.1.0

- `iconx add <package>` command: download icon packages (Lucide, Heroicons, Tabler, Phosphor, Bootstrap, Remix) directly from GitHub
- Style filtering: `iconx add heroicons/24`, `iconx add tabler/outline`
- Version pinning: `iconx add lucide --version v1.7.0`
- `GITHUB_TOKEN` support for higher GitHub API rate limits
- Auto-generates CSS after download (skip with `--no-generate`)
- **Breaking**: `iconx_generate` renamed to `iconx generate`

## 0.1.0a2

- CSS generation from SVG icon sources via `iconx_generate` management command
- Two embedding modes: `data_uri` (inline) and `url` (external, with `STATIC_URL` prefix)
- Multiple icon sets with configurable prefixes and regex-based path matching
- Mono icons via `mask-image` + `currentColor`, multi-color icons via `background-image`
- Automatic size variant detection from numbered subdirectories (e.g. `16/`, `24/`)
- Tailwind `text-*` class overrides that swap to the nearest size variant
- `--subset`, `--dry-run`, `--skip-name-collisions` CLI flags
- Django 5.2 and 6.0 support, Python 3.12+

## 0.1.0a1

Initial release.
