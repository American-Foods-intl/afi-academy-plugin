"""Connector settings: environment variables first, then ~/.afi-academy/connector.env."""
from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

NO_KEY = (
    "No Academy key yet: open Me → Connect Claude in the Academy and run the command it shows "
    "(it saves your key in ~/.afi-academy/connector.env)."
)
KEYS = ("ACADEMY_URL", "ACADEMY_TOKEN")


class ConfigMissing(Exception):
    pass


def _parse(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.lstrip("﻿").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
            v = v[1:-1]
        out[k.strip()] = v.strip()
    return out


def _file_values(home: Path) -> dict[str, str]:
    path = home / ".afi-academy" / "connector.env"
    try:
        return _parse(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeDecodeError) as e:
        reason = e.strerror if isinstance(e, OSError) and e.strerror else str(e)
        raise ConfigMissing(
            f"Your Academy key file ({path}) couldn't be read: {reason}. "
            "Run the command from Me → Connect Claude again."
        )


def load_config(env: Mapping[str, str] | None = None, home: Path | None = None) -> tuple[str, str]:
    """Return (url, token). Env vars override the file, per key. Raises ConfigMissing when either is absent."""
    env = os.environ if env is None else env
    home = Path.home() if home is None else home
    file_vals = {} if all((env.get(k) or "").strip() for k in KEYS) else _file_values(home)
    got = {k: (env.get(k) or "").strip() or file_vals.get(k, "").strip() for k in KEYS}
    if not got["ACADEMY_URL"] or not got["ACADEMY_TOKEN"]:
        raise ConfigMissing(NO_KEY)
    return got["ACADEMY_URL"].rstrip("/"), got["ACADEMY_TOKEN"]
