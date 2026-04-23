from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.conf import settings

VALID_MODES = ("data_uri", "url")
DEFAULT_PREFIX = "icon"


@dataclass(frozen=True)
class IconSet:
    path: str
    prefix: str = ""
    color: bool = False
    include_path: bool = False


@dataclass(frozen=True)
class IconxSettings:
    sets: list[IconSet] = field(default_factory=lambda: [IconSet("icons/")])
    output: str = "static/iconx/icons.css"
    mode: str = "url"
    prefix: str = DEFAULT_PREFIX
    size: str = "1em"

    def __post_init__(self) -> None:
        if self.mode not in VALID_MODES:
            msg = f"Invalid mode {self.mode!r}, must be one of {VALID_MODES}"
            raise ValueError(msg)


def _normalize_sets(raw_sets: list[str | dict[str, Any]]) -> list[IconSet]:
    """Normalize set config: strings become IconSet(path=...), dicts become IconSet(**...)."""
    return [IconSet(path=s) if isinstance(s, str) else IconSet(**s) for s in raw_sets]


def get_settings() -> IconxSettings:
    raw: dict[str, Any] = getattr(settings, "ICONX", {})
    if "sets" in raw:
        raw = {**raw, "sets": _normalize_sets(raw["sets"])}
    return IconxSettings(**raw)
