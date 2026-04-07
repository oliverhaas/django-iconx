from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from django_iconx.conf import get_settings
from django_iconx.css import generate_css
from django_iconx.download import download_package
from django_iconx.svg import discover


class Command(BaseCommand):
    help = "Manage icon packages and generate CSS"

    def add_arguments(self, parser: CommandParser) -> None:
        subparsers = parser.add_subparsers(dest="subcommand")

        # --- add ---
        add_parser = subparsers.add_parser("add", help="Download an icon package from GitHub")
        add_parser.add_argument(
            "package",
            help="Package name, e.g. 'lucide', 'heroicons/24', 'tabler/outline'",
        )
        add_parser.add_argument(
            "--version",
            help="Specific version tag (default: latest release)",
        )
        add_parser.add_argument(
            "--no-generate",
            action="store_true",
            help="Skip CSS generation after download",
        )

        # --- generate ---
        gen_parser = subparsers.add_parser("generate", help="Generate CSS file from SVG icons")
        gen_parser.add_argument(
            "--output",
            type=str,
            help="Override output file path (default: from ICONX settings)",
        )
        gen_parser.add_argument(
            "--mode",
            choices=["data_uri", "url"],
            help="Override icon embedding mode (default: from ICONX settings)",
        )
        gen_parser.add_argument(
            "--subset",
            type=str,
            help="Comma-separated list of icon names to include",
        )
        gen_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print CSS to stdout instead of writing to file",
        )
        gen_parser.add_argument(
            "--skip-name-collisions",
            action="store_true",
            help="Warn on icon name collisions instead of aborting",
        )

    def handle(self, **options: Any) -> None:  # noqa: ANN401
        subcommand = options.get("subcommand")
        if subcommand == "add":
            self._handle_add(**options)
        elif subcommand == "generate":
            self._handle_generate(**options)
        else:
            self.print_help("manage.py", "iconx")

    def _handle_add(self, **options: Any) -> None:  # noqa: ANN401
        static_dirs = getattr(settings, "STATICFILES_DIRS", [])
        if not static_dirs:
            msg = "STATICFILES_DIRS is not configured. Add at least one directory to your Django settings."
            raise CommandError(msg)

        first_dir = static_dirs[0]
        if isinstance(first_dir, (list, tuple)):
            first_dir = first_dir[1]

        spec: str = options["package"]
        name = spec.split("/", 1)[0]
        target_dir = Path(first_dir) / "icons" / name

        result = download_package(spec, target_dir, version=options.get("version"))

        self.stdout.write(
            self.style.SUCCESS(f"Downloaded {result.icon_count} icons from {result.package} {result.version}"),
        )
        self.stdout.write(f"  {result.target_dir}")

        if not options.get("no_generate"):
            self._handle_generate(**options)

    def _handle_generate(self, **options: Any) -> None:  # noqa: ANN401
        icon_settings = get_settings()

        overrides: dict[str, Any] = {}
        if options.get("output"):
            overrides["output"] = options["output"]
        if options.get("mode"):
            overrides["mode"] = options["mode"]
        if overrides:
            icon_settings = replace(icon_settings, **overrides)

        subset: set[str] | None = None
        if options.get("subset"):
            subset = {s.strip() for s in options["subset"].split(",")}

        try:
            discovered = discover(icon_settings, skip_collisions=options.get("skip_name_collisions", False))
        except ValueError as e:
            self.stderr.write(self.style.ERROR(str(e)))
            return
        if not discovered.icons:
            self.stderr.write(self.style.WARNING("No SVG icons found in configured sets."))
            return

        css = generate_css(icon_settings, subset=subset, discovered=discovered)

        if options.get("dry_run"):
            self.stdout.write(css)
            return

        output_path = Path(icon_settings.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(css, encoding="utf-8")

        icon_count = len(discovered.icons) if subset is None else len(subset & discovered.icons.keys())
        self.stdout.write(
            self.style.SUCCESS(f"Generated {output_path} with {icon_count} icons ({icon_settings.mode} mode)"),
        )
