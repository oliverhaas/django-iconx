from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.conf import settings


@dataclass(frozen=True)
class IconxSettings:
    sets: dict[str, str] = field(default_factory=lambda: {"": "icons/"})
    output: str = "static/iconx/icons.css"
    mode: str = "data_uri"
    prefix: str = "icon"
    size: str = "1em"

    def __post_init__(self) -> None:
        if self.mode not in ("data_uri", "url"):
            msg = f"Invalid mode {self.mode!r}, must be 'data_uri' or 'url'"
            raise ValueError(msg)


def get_settings() -> IconxSettings:
    raw: dict[str, Any] = getattr(settings, "ICONX", {})
    return IconxSettings(**raw)
