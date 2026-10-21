"""Thin HTTP client for the Academy connector API. Never logs the token."""
from __future__ import annotations

import mimetypes
from pathlib import Path

import httpx

TIMEOUT = 30.0
UPLOAD_TIMEOUT = 900.0  # above the server's 600 s conversion deadline
MB = 1024 * 1024
MAX_IMAGE_BYTES = 10 * MB
MAX_AUDIO_BYTES = 50 * MB
MAX_VTT_BYTES = 1 * MB
MAX_VIDEO_BYTES = 400 * MB
MAX_HEIC_BYTES = 25 * MB
HEIC_EXT = {".heic", ".heif"}  # iPhone photos: the Academy converts them to JPEG on upload
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"} | HEIC_EXT
AUDIO_EXT = {".m4a", ".mp3"}
PROVENANCE = ("photo", "screenshot", "drawn", "generated")
ALLOWED = "png, jpg, jpeg, webp, gif, heic, heif, mp4, mov, m4a, mp3 or vtt"


def _cap(ext: str) -> tuple[str, int]:
    if ext in HEIC_EXT:
        return "image", MAX_HEIC_BYTES
    if ext in IMAGE_EXT:
        return "image", MAX_IMAGE_BYTES
    if ext in AUDIO_EXT:
        return "audio", MAX_AUDIO_BYTES
    if ext == ".vtt":
        return "captions", MAX_VTT_BYTES
    return "video", MAX_VIDEO_BYTES


class AcademyClient:
    def __init__(self, base_url: str, token: str, http: httpx.Client | None = None):
        self.base = base_url.rstrip("/") + "/api/connector"
        self._headers = {"Authorization": f"Bearer {token}"}
        self.http = http or httpx.Client(timeout=TIMEOUT)

    def _call(self, method: str, path: str, timeout: float = TIMEOUT, **kw) -> dict:
        try:
            r = self.http.request(method, self.base + path, headers=self._headers, timeout=timeout, **kw)
        except httpx.HTTPError as e:
            return {"error": f"cannot reach the Academy: {type(e).__name__}: {e}"}
        if r.is_success:
            try:
                return r.json()
            except ValueError:
                return {"error": "the Academy returned a non-JSON answer", "status": r.status_code}
        try:
            detail = r.json().get("detail")
        except (ValueError, AttributeError):
            detail = None
        return {"error": detail or r.reason_phrase or f"HTTP {r.status_code}", "status": r.status_code}

    def kit(self) -> dict:
        return self._call("GET", "/kit")

    def validate(self, course: dict) -> dict:
        return self._call("POST", "/validate", json={"course": course})

    def validate_brief(self, brief: dict) -> dict:
        return self._call("POST", "/brief/validate", json={"brief": brief})

    def upload_media(self, path: str, provenance: str | None = None) -> dict:
        p = Path(path).expanduser()
        if not p.is_file():
            return {"error": f"file not found: {path}"}
        ext = p.suffix.lower()
        if ext not in IMAGE_EXT | AUDIO_EXT | {".vtt", ".mp4", ".mov"}:
            return {"error": f"{p.name} is not allowed: use {ALLOWED}"}
        if ext in IMAGE_EXT and provenance not in PROVENANCE:
            return {"error": "images need provenance: one of " + ", ".join(PROVENANCE)
                             + " (photo/screenshot = real; drawn/generated = made up)"
                             + (f" — got {provenance!r}" if provenance else "")}
        kind, cap = _cap(ext)
        if p.stat().st_size > cap:
            return {"error": f"{p.name} is too large (max {cap // MB} MB for {kind} files)"}
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        data = {"provenance": provenance} if provenance in PROVENANCE else None
        with p.open("rb") as fh:  # streamed, never read into memory
            out = self._call("POST", "/media", timeout=UPLOAD_TIMEOUT,
                             files={"file": (p.name, fh, ctype)}, data=data)
        if "error" in out:
            return out
        return {k: out[k] for k in ("src", "sha256", "content_type", "bytes", "provenance") if k in out}

    def request_render(self, spec: dict) -> dict:
        return self._call("POST", "/renders", json={"spec": spec})

    def get_render(self, job_id: str) -> dict:
        return self._call("GET", f"/renders/{job_id}")

    def save_draft(self, course: dict, note: str | None = None, draft_id: str | None = None,
                   change: str | None = None) -> dict:
        body: dict = {"course": course, "note": note}
        if draft_id:
            body["draft_id"] = draft_id
        if change:
            body["change"] = change
        return self._call("POST", "/drafts", json=body)

    def get_course(self, course_id: str) -> dict:
        return self._call("GET", f"/courses/{course_id}")

    def start_update(self, course_id: str, change: str, note: str) -> dict:
        return self._call("POST", f"/courses/{course_id}/drafts", json={"change": change, "note": note})

    def get_draft(self, draft_id: str) -> dict:
        return self._call("GET", f"/drafts/{draft_id}")

    def list_courses(self) -> dict:
        return self._call("GET", "/courses")

    def mark_ready(self, draft_id: str) -> dict:
        return self._call("POST", f"/drafts/{draft_id}/ready")
