from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from django_iconx.conf import get_settings
from django_iconx.css import generate_css
from django_iconx.svg import discover


class Command(BaseCommand):
    help = "Generate CSS file from configured SVG icon sets"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--output",
            type=str,
            help="Override output file path (default: from ICONX settings)",
        )
        parser.add_argument(
            "--mode",
            choices=["data_uri", "url"],
            help="Override icon embedding mode (default: from ICONX settings)",
        )
        parser.add_argument(
            "--subset",
            type=str,
            help="Comma-separated list of icon names to include",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print CSS to stdout instead of writing to file",
        )

    def handle(self, **options: Any) -> None:  # noqa: ANN401
        icon_settings = get_settings()

        # Apply CLI overrides
        overrides: dict[str, Any] = {}
        if options["output"]:
            overrides["output"] = options["output"]
        if options["mode"]:
            overrides["mode"] = options["mode"]
        if overrides:
            icon_settings = replace(icon_settings, **overrides)

        # Parse subset
        subset: set[str] | None = None
        if options["subset"]:
            subset = {s.strip() for s in options["subset"].split(",")}

        # Discover icons (single scan, shared with generate_css)
        try:
            discovered = discover(icon_settings)
        except ValueError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return
        if not discovered.icons:
            self.stderr.write(self.style.WARNING("No SVG icons found in configured sets."))
            return

        # Generate CSS
        css = generate_css(icon_settings, subset=subset, discovered=discovered)

        if options["dry_run"]:
            self.stdout.write(css)
            return

        # Write output
        output_path = Path(icon_settings.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(css, encoding="utf-8")

        icon_count = len(discovered.icons) if subset is None else len(subset & discovered.icons.keys())
        self.stdout.write(
            self.style.SUCCESS(f"Generated {output_path} with {icon_count} icons ({icon_settings.mode} mode)"),
        )
