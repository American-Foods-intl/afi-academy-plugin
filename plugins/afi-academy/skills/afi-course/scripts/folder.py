# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Course folder state for the /afi-course skill.

Folders live under $AFI_ACADEMY_HOME or ~/AFI Academy/<slug>/. CLI:
    uv run folder.py <cmd> --json '<args as a JSON object>'
Prints JSON on stdout; on failure exits 1 with {"error": "..."} on stderr.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

PHASES = ("intake", "brief", "gather", "write", "saved", "review")
ROLES = ("source", "photo", "screenshot", "video", "audio")
NEED_KINDS = ("fact", "photo", "screenshot", "expert", "other")
NEED_STATUSES = ("open", "done", "waived")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def root() -> Path:
    env = os.environ.get("AFI_ACADEMY_HOME")
    return Path(env) if env else Path.home() / "AFI Academy"


def _dir(slug: str) -> Path:
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise ValueError(f"invalid slug: {slug!r}")
    return root() / slug


def _course_dir(slug: str) -> Path:
    d = _dir(slug)
    if not (d / "state.json").is_file():
        raise ValueError(f"no such course: {slug}")
    return d


def _write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data) -> None:
    _write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def init_course(slug: str, title: str) -> Path:
    d = _dir(slug)
    if d.exists():
        raise ValueError(f"course folder already exists: {slug}")
    (d / "assets").mkdir(parents=True)
    _write_json(d / "assets.json", [])
    _write_json(d / "needs.json", [])
    _write(d / "log.md", f"# {title}\n")
    _write_json(d / "state.json", {
        "slug": slug, "title": title, "phase": "intake", "brief_version": 0,
        "approved_version": None, "draft_id": None, "revision": None,
        "pending_renders": [], "updated_at": _now(),
    })
    return d


def list_courses() -> list[dict]:
    rows = []
    r = root()
    if r.is_dir():
        for d in r.iterdir():
            sp = d / "state.json"
            if sp.is_file():
                try:
                    st = _read_json(sp)
                except ValueError:
                    continue
                row = {k: st.get(k) for k in ("slug", "phase", "brief_version", "draft_id",
                                              "updated_at", "update_of", "course_id")}
                row["pending_renders"] = st.get("pending_renders") or []
                rows.append(row)
    rows.sort(key=lambda x: x["updated_at"] or "", reverse=True)
    return rows


def get_state(slug: str) -> dict:
    return _read_json(_course_dir(slug) / "state.json")


def set_state(slug: str, **changes) -> dict:
    d = _course_dir(slug)
    if "phase" in changes and changes["phase"] not in PHASES:
        raise ValueError(f"phase must be one of {', '.join(PHASES)}")
    st = _read_json(d / "state.json")
    st.update(changes)
    st["updated_at"] = _now()
    _write_json(d / "state.json", st)
    return st


def _asset_name(d: Path, file: str) -> str:
    base = (d / "assets").resolve()
    p = Path(file)
    if not p.is_absolute() and p.parts[:1] == ("assets",):
        p = Path(*p.parts[1:]) if len(p.parts) > 1 else p
    full = p if p.is_absolute() else base / p
    full = Path(os.path.normpath(full))
    try:
        rel = full.resolve().relative_to(base)
    except ValueError:
        raise ValueError(f"file must be inside assets/: {file}") from None
    if not rel.parts:
        raise ValueError(f"file must be inside assets/: {file}")
    return rel.as_posix()


def add_asset(slug: str, file: str, role: str, provenance=None,
              authoritative: bool = False, rights: str = "", notes: str = "") -> dict:
    d = _course_dir(slug)
    if role not in ROLES:
        raise ValueError(f"role must be one of {', '.join(ROLES)}")
    name = _asset_name(d, file)
    entry = {"file": name, "role": role, "provenance": provenance,
             "authoritative": bool(authoritative), "rights": rights,
             "notes": notes, "src": None}
    assets = _read_json(d / "assets.json")
    for i, a in enumerate(assets):
        if a["file"] == name:
            entry["src"] = a.get("src")
            assets[i] = entry
            break
    else:
        assets.append(entry)
    _write_json(d / "assets.json", assets)
    return entry


def set_asset_src(slug: str, file: str, src) -> dict:
    d = _course_dir(slug)
    name = _asset_name(d, file)
    assets = _read_json(d / "assets.json")
    for a in assets:
        if a["file"] == name:
            a["src"] = src
            _write_json(d / "assets.json", assets)
            return a
    raise ValueError(f"asset not tracked: {name}")


SYSTEM_FILES = {"thumbs.db", "desktop.ini"}


def _is_system_file(rel: Path) -> bool:
    """Dotfiles, anything inside a dot-directory, and Windows' Thumbs.db / desktop.ini."""
    return any(part.startswith(".") for part in rel.parts) or rel.name.lower() in SYSTEM_FILES


def untracked_assets(slug: str) -> list[str]:
    d = _course_dir(slug)
    tracked = {a["file"] for a in _read_json(d / "assets.json")}
    base = d / "assets"
    found = (p.relative_to(base) for p in base.rglob("*") if p.is_file())
    return sorted(f.as_posix() for f in found
                  if not _is_system_file(f) and f.as_posix() not in tracked)


def set_needs(slug: str, items: list) -> list:
    """Write the needs list. Ids already in needs.json keep their status and note; new ids start open; ids no
    longer listed are dropped."""
    d = _course_dir(slug)
    old = {n["id"]: n for n in _read_json(d / "needs.json")}
    out = []
    for it in items:
        if it.get("kind") not in NEED_KINDS:
            raise ValueError(f"kind must be one of {', '.join(NEED_KINDS)}")
        prev = old.get(it["id"], {})
        need = {"id": it["id"], "text": it["text"], "who": it["who"],
                "kind": it["kind"], "status": prev.get("status", "open")}
        if "note" in prev:
            need["note"] = prev["note"]
        out.append(need)
    if len({i["id"] for i in out}) != len(out):
        raise ValueError("duplicate need id")
    _write_json(d / "needs.json", out)
    return out


def mark_need(slug: str, id: str, status: str, note: str = "") -> dict:
    d = _course_dir(slug)
    if status not in NEED_STATUSES:
        raise ValueError(f"status must be one of {', '.join(NEED_STATUSES)}")
    needs = _read_json(d / "needs.json")
    for n in needs:
        if n["id"] == id:
            n["status"] = status
            if note:
                n["note"] = note
            _write_json(d / "needs.json", needs)
            return n
    raise ValueError(f"no such need: {id}")


def open_needs(slug: str) -> list:
    return [n for n in _read_json(_course_dir(slug) / "needs.json")
            if n["status"] == "open"]


def log(slug: str, line: str) -> dict:
    d = _course_dir(slug)
    p = d / "log.md"
    text = p.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    _write(p, text + f"- {_now()} {line}\n")
    return {"ok": True}


def suggest_slug(title: str, taken: list) -> str:
    ascii_ = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")[:64].strip("-")
    if len(base) < 2:
        base = "course"
    taken = set(taken)
    if base not in taken:
        return base
    n = 2
    while True:
        suffix = f"-{n}"
        cand = base[:64 - len(suffix)].rstrip("-") + suffix
        if cand not in taken:
            return cand
        n += 1


COMMANDS = {
    "root": root, "init-course": init_course, "list-courses": list_courses,
    "list": list_courses, "get-state": get_state, "set-state": set_state,
    "add-asset": add_asset, "set-asset-src": set_asset_src,
    "untracked-assets": untracked_assets, "set-needs": set_needs,
    "mark-need": mark_need, "open-needs": open_needs, "log": log,
    "suggest-slug": suggest_slug,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=sorted(COMMANDS))
    ap.add_argument("--json", dest="args", default="{}",
                    help="arguments as a JSON object")
    ns = ap.parse_args(argv)
    try:
        args = json.loads(ns.args)
        if not isinstance(args, dict):
            raise ValueError("--json must be a JSON object")
        result = COMMANDS[ns.cmd](**args)
    except (ValueError, TypeError, KeyError, OSError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1
    if isinstance(result, Path):
        result = str(result)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
