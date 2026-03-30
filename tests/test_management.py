from __future__ import annotations

from pathlib import Path

from django.core.management import call_command
from django.test import override_settings

FIXTURES = Path(__file__).parent / "fixtures"


class TestIconxGenerateCommand:
    @override_settings(ICONX={"sets": {"": str(FIXTURES / "icons")}})
    def test_dry_run(self, capsys):
        call_command("iconx_generate", dry_run=True)
        output = capsys.readouterr().out
        assert ".icon::before {" in output
        assert ".icon-search::before {" in output

    @override_settings(ICONX={"sets": {"": str(FIXTURES / "icons")}})
    def test_writes_file(self, tmp_path):
        output_file = tmp_path / "icons.css"
        call_command("iconx_generate", output=str(output_file))
        assert output_file.exists()
        css = output_file.read_text()
        assert ".icon-search::before {" in css

    @override_settings(ICONX={"sets": {"": str(FIXTURES / "icons")}})
    def test_subset(self, capsys):
        call_command("iconx_generate", dry_run=True, subset="search")
        output = capsys.readouterr().out
        assert ".icon-search::before {" in output
        assert ".icon-x::before {" not in output

    @override_settings(ICONX={"sets": {"": "/nonexistent"}})
    def test_no_icons_warning(self, capsys):
        call_command("iconx_generate")
        err = capsys.readouterr().err
        assert "No SVG icons found" in err
