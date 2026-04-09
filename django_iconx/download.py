from __future__ import annotations

import io
import json
import logging
import os
import shutil
import zipfile
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.management.base import CommandError

from django_iconx.registry import REGISTRY

if TYPE_CHECKING:
    from pathlib import Path

    from django_iconx.registry import IconPackage

logger = logging.getLogger("django_iconx")

GITHUB_API = "https://api.github.com/repos"
GITHUB_ARCHIVE = "https://github.com"
TIMEOUT = 30


@dataclass
class DownloadResult:
    package: str
    version: str
    icon_count: int
    target_dir: Path


def parse_package_spec(spec: str) -> tuple[str, str | None]:
    """Split 'heroicons/24' into ('heroicons', '24'). Plain 'lucide' returns ('lucide', None)."""
    if "/" in spec:
        name, style = spec.split("/", 1)
        return name, style
    return spec, None


def download_package(
    spec: str,
    target_dir: Path,
    *,
    version: str | None = None,
) -> DownloadResult:
    """Download an icon package from GitHub and extract SVGs to target_dir."""
    name, style = parse_package_spec(spec)
    pkg = _resolve_package(name)

    if style and pkg.styles and style not in pkg.styles:
        available = ", ".join(pkg.styles)
        msg = f"Unknown style '{style}' for {name}. Available: {available}"
        raise CommandError(msg)
    if style and not pkg.styles:
        msg = f"Package '{name}' has no styles (flat structure). Remove the '/{style}' suffix."
        raise CommandError(msg)

    tag = version or _get_latest_version(pkg.repo)
    zip_buf = _download_zip(pkg.repo, tag)
    count = _extract_svgs(zip_buf, pkg.svg_path, style, target_dir)

    return DownloadResult(package=name, version=tag, icon_count=count, target_dir=target_dir)


def _resolve_package(name: str) -> IconPackage:
    if name not in REGISTRY:
        available = ", ".join(sorted(REGISTRY))
        msg = f"Unknown package '{name}'. Available: {available}"
        raise CommandError(msg)
    return REGISTRY[name]


def _github_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_latest_version(repo: str) -> str:
    url = f"{GITHUB_API}/{repo}/releases/latest"
    req = Request(url, headers=_github_headers())  # noqa: S310
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310
            data = json.loads(resp.read())
    except HTTPError as e:
        if e.code == 403:  # noqa: PLR2004
            msg = (
                f"GitHub API rate limit hit for {repo}. "
                "Pass --version <tag> to skip the API call, "
                "or set GITHUB_TOKEN to raise the limit."
            )
            raise CommandError(msg) from e
        msg = f"Failed to fetch latest version for {repo}: {e}"
        raise CommandError(msg) from e
    except URLError as e:
        msg = f"Failed to fetch latest version for {repo}: {e}"
        raise CommandError(msg) from e
    return data["tag_name"]


def _download_zip(repo: str, tag: str) -> io.BytesIO:
    url = f"{GITHUB_ARCHIVE}/{repo}/archive/refs/tags/{tag}.zip"
    try:
        with urlopen(url, timeout=TIMEOUT) as resp:  # noqa: S310
            return io.BytesIO(resp.read())
    except (URLError, HTTPError) as e:
        msg = f"Failed to download {repo} {tag}: {e}"
        raise CommandError(msg) from e


def _find_archive_root(zf: zipfile.ZipFile) -> str:
    """Find the single root directory in a GitHub archive zip."""
    roots = {n.split("/")[0] for n in zf.namelist() if "/" in n}
    if len(roots) != 1:
        msg = f"Unexpected archive structure: found {len(roots)} root directories"
        raise CommandError(msg)
    return roots.pop() + "/"


def _extract_svgs(
    zip_buf: io.BytesIO,
    svg_path: str,
    style: str | None,
    target_dir: Path,
) -> int:
    """Extract .svg files from the zip to target_dir. Returns count of extracted files."""
    with zipfile.ZipFile(zip_buf) as zf:
        root = _find_archive_root(zf)
        prefix = f"{root}{svg_path}"
        if style:
            prefix = f"{prefix}{style}/"

        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True)

        count = 0
        for entry in zf.namelist():
            if not entry.startswith(prefix) or not entry.endswith(".svg"):
                continue
            relative = entry[len(prefix) :]
            if not relative:
                continue
            dest = target_dir / relative
            if not dest.resolve().is_relative_to(target_dir.resolve()):
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(zf.read(entry))
            count += 1

    return count
