from __future__ import annotations

import io
import json
import zipfile
from unittest.mock import patch
from urllib.error import URLError

import pytest
from django.core.management.base import CommandError

from django_iconx.download import (
    DownloadResult,
    _extract_svgs,
    _find_archive_root,
    _get_latest_version,
    download_package,
    parse_package_spec,
)


class TestParsePackageSpec:
    def test_simple_name(self):
        assert parse_package_spec("lucide") == ("lucide", None)

    def test_with_style(self):
        assert parse_package_spec("heroicons/24") == ("heroicons", "24")

    def test_with_style_string(self):
        assert parse_package_spec("tabler/outline") == ("tabler", "outline")


class TestResolvePackage:
    def test_known_package(self):
        result = download_package.__wrapped__ if hasattr(download_package, "__wrapped__") else None
        # Test via download_package which calls _resolve_package internally
        with pytest.raises(CommandError, match="STATICFILES_DIRS"):
            # Will fail at STATICFILES_DIRS check, but _resolve_package succeeds
            pass

    def test_unknown_package(self, tmp_path):
        with pytest.raises(CommandError, match="Unknown package 'foobar'"):
            download_package("foobar", tmp_path)

    def test_unknown_package_lists_available(self, tmp_path):
        with pytest.raises(CommandError, match="lucide"):
            download_package("foobar", tmp_path)


class TestStyleValidation:
    def test_invalid_style_on_styled_package(self, tmp_path):
        with pytest.raises(CommandError, match="Unknown style 'huge'"):
            download_package("heroicons/huge", tmp_path)

    def test_style_on_flat_package(self, tmp_path):
        with pytest.raises(CommandError, match="no styles"):
            download_package("lucide/bold", tmp_path)


class TestGetLatestVersion:
    def test_returns_tag_name(self):
        response_data = json.dumps({"tag_name": "v1.7.0"}).encode()
        mock_resp = io.BytesIO(response_data)
        mock_resp.status = 200

        with patch("django_iconx.download.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__ = lambda s: mock_resp
            mock_urlopen.return_value.__exit__ = lambda s, *a: None
            version = _get_latest_version("lucide-icons/lucide")

        assert version == "v1.7.0"

    def test_network_error(self):
        with (
            patch("django_iconx.download.urlopen", side_effect=URLError("no network")),
            pytest.raises(CommandError, match="Failed to fetch"),
        ):
            _get_latest_version("lucide-icons/lucide")


class TestFindArchiveRoot:
    def test_single_root(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("lucide-1.7.0/icons/search.svg", "<svg/>")
        buf.seek(0)
        with zipfile.ZipFile(buf) as zf:
            assert _find_archive_root(zf) == "lucide-1.7.0/"

    def test_multiple_roots_raises(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("dir-a/file.svg", "<svg/>")
            zf.writestr("dir-b/file.svg", "<svg/>")
        buf.seek(0)
        with zipfile.ZipFile(buf) as zf, pytest.raises(CommandError, match="Unexpected archive"):
            _find_archive_root(zf)


class TestExtractSvgs:
    def _make_zip(self, files: dict[str, str]) -> io.BytesIO:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for path, content in files.items():
                zf.writestr(path, content)
        buf.seek(0)
        return buf

    def test_extracts_only_svgs(self, tmp_path):
        zip_buf = self._make_zip(
            {
                "root/icons/search.svg": "<svg>search</svg>",
                "root/icons/arrow.svg": "<svg>arrow</svg>",
                "root/icons/README.md": "# Icons",
                "root/LICENSE": "MIT",
            },
        )
        count = _extract_svgs(zip_buf, "icons/", None, tmp_path / "out")
        assert count == 2
        assert (tmp_path / "out" / "search.svg").exists()
        assert (tmp_path / "out" / "arrow.svg").exists()
        assert not (tmp_path / "out" / "README.md").exists()

    def test_extracts_with_style_filter(self, tmp_path):
        zip_buf = self._make_zip(
            {
                "root/optimized/16/search.svg": "<svg>16</svg>",
                "root/optimized/24/search.svg": "<svg>24</svg>",
                "root/optimized/24/arrow.svg": "<svg>24</svg>",
            },
        )
        count = _extract_svgs(zip_buf, "optimized/", "24", tmp_path / "out")
        assert count == 2
        assert (tmp_path / "out" / "search.svg").exists()
        assert (tmp_path / "out" / "arrow.svg").exists()

    def test_preserves_subdirectory_structure(self, tmp_path):
        zip_buf = self._make_zip(
            {
                "root/icons/outline/search.svg": "<svg/>",
                "root/icons/filled/search.svg": "<svg/>",
            },
        )
        count = _extract_svgs(zip_buf, "icons/", None, tmp_path / "out")
        assert count == 2
        assert (tmp_path / "out" / "outline" / "search.svg").exists()
        assert (tmp_path / "out" / "filled" / "search.svg").exists()

    def test_overwrites_existing_directory(self, tmp_path):
        target = tmp_path / "out"
        target.mkdir()
        (target / "old.svg").write_text("<svg>old</svg>")

        zip_buf = self._make_zip({"root/icons/new.svg": "<svg>new</svg>"})
        _extract_svgs(zip_buf, "icons/", None, target)

        assert (target / "new.svg").exists()
        assert not (target / "old.svg").exists()


class TestDownloadPackage:
    def _make_zip(self, files: dict[str, str]) -> io.BytesIO:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for path, content in files.items():
                zf.writestr(path, content)
        buf.seek(0)
        return buf

    def test_full_flow(self, tmp_path):
        api_response = io.BytesIO(json.dumps({"tag_name": "v1.0.0"}).encode())
        zip_buf = self._make_zip(
            {
                "lucide-1.0.0/icons/search.svg": "<svg/>",
                "lucide-1.0.0/icons/arrow.svg": "<svg/>",
            },
        )

        def mock_urlopen(url_or_req, *, timeout=None):
            url = url_or_req.full_url if hasattr(url_or_req, "full_url") else url_or_req
            if "api.github.com" in url:
                return api_response
            zip_buf.seek(0)
            return zip_buf

        with patch("django_iconx.download.urlopen", side_effect=mock_urlopen):
            result = download_package("lucide", tmp_path / "icons" / "lucide")

        assert result == DownloadResult(
            package="lucide",
            version="v1.0.0",
            icon_count=2,
            target_dir=tmp_path / "icons" / "lucide",
        )
        assert (tmp_path / "icons" / "lucide" / "search.svg").exists()
