from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import override_settings

from django_iconx.download import DownloadResult

FIXTURES = Path(__file__).parent / "fixtures"


class TestIconxGenerate:
    @override_settings(ICONX={"sets": ["icons/"]})
    def test_dry_run(self, capsys):
        call_command("iconx", "generate", dry_run=True)
        output = capsys.readouterr().out
        assert ".icon {" in output
        assert ".icon-search {" in output

    @override_settings(ICONX={"sets": ["icons/"]})
    def test_writes_file(self, tmp_path):
        output_file = tmp_path / "icons.css"
        call_command("iconx", "generate", output=str(output_file))
        assert output_file.exists()
        css = output_file.read_text()
        assert ".icon-search {" in css

    @override_settings(ICONX={"sets": ["icons/"]})
    def test_subset(self, capsys):
        call_command("iconx", "generate", dry_run=True, subset="search")
        output = capsys.readouterr().out
        assert ".icon-search {" in output
        assert ".icon-x" not in output

    @override_settings(ICONX={"sets": ["nonexistent/"]})
    def test_no_icons_warning(self, capsys):
        call_command("iconx", "generate")
        err = capsys.readouterr().err
        assert "No SVG icons found" in err


class TestIconxAdd:
    @override_settings(ICONX={"sets": ["icons/"]})
    def test_add_downloads_and_generates(self, capsys, tmp_path, settings):
        settings.STATICFILES_DIRS = [str(tmp_path)]
        target = tmp_path / "icons" / "lucide"
        fake_result = DownloadResult(package="lucide", version="v1.0.0", icon_count=5, target_dir=target)

        with patch("django_iconx.management.commands.iconx.download_package", return_value=fake_result):
            call_command("iconx", "add", "lucide", no_generate=True)

        output = capsys.readouterr().out
        assert "5 icons" in output
        assert "lucide" in output

    @override_settings(ICONX={"sets": ["icons/"]})
    def test_add_no_generate_skips_css(self, capsys, tmp_path, settings):
        settings.STATICFILES_DIRS = [str(tmp_path)]
        target = tmp_path / "icons" / "lucide"
        fake_result = DownloadResult(package="lucide", version="v1.0.0", icon_count=5, target_dir=target)

        with (
            patch("django_iconx.management.commands.iconx.download_package", return_value=fake_result),
            patch("django_iconx.management.commands.iconx.generate_css") as mock_gen,
        ):
            call_command("iconx", "add", "lucide", no_generate=True)
            mock_gen.assert_not_called()
