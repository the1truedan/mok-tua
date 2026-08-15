"""mok-tua conductor TUI — C64 (default) + standard mono skins over CLI verbs."""

from __future__ import annotations

__version__ = "0.6.0"

# Canonical skin ids (map to themes/*.tcss)
SKINS = (
    "c64",
    "modern",
    "green",
    "mono",
    # aliases accepted via resolve_skin
    "1980crt",
    "tui-c64-mode-default-1980crt-tui",
    "matrix",
    "paper",
)

DEFAULT_SKIN = "c64"

_SKIN_ALIASES: dict[str, str] = {
    "c64": "c64",
    "1980crt": "c64",
    "tui-c64-mode-default-1980crt-tui": "c64",
    "modern": "modern",
    "green": "green",
    "matrix": "green",
    "mono": "mono",
    "paper": "mono",
}


def resolve_skin(name: str | None) -> str:
    if not name:
        return DEFAULT_SKIN
    key = name.strip().lower()
    return _SKIN_ALIASES.get(key, key if key in _SKIN_ALIASES.values() else DEFAULT_SKIN)
