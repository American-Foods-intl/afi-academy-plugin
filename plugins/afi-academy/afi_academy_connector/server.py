"""AFI Academy connector: a local stdio MCP server.

Settings: ACADEMY_URL and ACADEMY_TOKEN, from the environment or, when not set, from the per-user file
~/.afi-academy/connector.env. The environment wins.
"""
from __future__ import annotations

import functools
import json
from pathlib import Path

import httpx
from mcp.server.mcpserver import MCPServer

from .client import TIMEOUT, AcademyClient
from .config import ConfigMissing, load_config

MAX_COURSE_BYTES = 5 * 1024 * 1024
MAX_SPEC_BYTES = 1024 * 1024
CHANGES = ("small", "material")
mcp = MCPServer("afi-academy")
HTTP: httpx.Client | None = None  # tests inject a MockTransport client


class _Fail(Exception):
    pass


@functools.cache
def _shared_http() -> httpx.Client:
    """One connection pool for the server's lifetime: no new TLS handshake per tool call."""
    return httpx.Client(timeout=TIMEOUT)


def _client() -> AcademyClient:
    try:
        url, token = load_config()  # read per call, so a new key works without restarting Claude
    except ConfigMissing as e:
        raise _Fail(str(e))
    return AcademyClient(url, token, HTTP or _shared_http())


def _course(course: dict | str) -> dict:
    if isinstance(course, dict):
        if len(json.dumps(course).encode()) > MAX_COURSE_BYTES:
            raise _Fail(f"course JSON is too large (max {MAX_COURSE_BYTES // 1024 // 1024} MB)")
        return course
    p = Path(str(course)).expanduser()
    if not p.is_file():
        raise _Fail(f"course file not found: {course}")
    if p.stat().st_size > MAX_COURSE_BYTES:
        raise _Fail(f"{p.name} is too large (max {MAX_COURSE_BYTES // 1024 // 1024} MB)")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise _Fail(f"{p.name} is not valid JSON: {e}")
    if not isinstance(data, dict):
        raise _Fail(f"{p.name} must hold a JSON object (the course)")
    return data


def _spec(spec: dict | str) -> dict:
    if isinstance(spec, dict):
        return spec
    p = Path(str(spec)).expanduser()
    if not p.is_file():
        raise _Fail(f"spec file not found: {spec}")
    if p.stat().st_size > MAX_SPEC_BYTES:
        raise _Fail(f"{p.name} is too large (max 1 MB)")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise _Fail(f"{p.name} is not valid JSON: {e}")
    if not isinstance(data, dict):
        raise _Fail(f"{p.name} must hold a JSON object (the render spec)")
    return data


def _change(change: str | None, required: bool = True) -> None:
    if (change is not None or required) and change not in CHANGES:
        raise _Fail(f"change must be small or material — got {change!r}")


def _errors(fn):
    @functools.wraps(fn)
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except _Fail as e:
            return {"error": str(e)}
        except Exception as e:  # noqa: BLE001 — tool results are data, never a crashed server
            return {"error": f"{type(e).__name__}: {e}"}
    return wrapper


@mcp.tool()
@_errors
def academy_kit() -> dict:
    """START HERE. Returns the course kit: JSON schema, block catalog, writing guide and a worked example.
    Workflow: 1) get the kit, 2) write the course JSON per the schema (English and Spanish for every text),
    3) upload photos/video/audio with academy_upload_media (images need provenance) or make media with
    academy_request_render, and use the returned src/outputs, 4) academy_validate until clean,
    5) academy_save_draft, 6) give the author the preview_url to review. Publishing is done by a person in the
    Academy; Claude cannot publish.
    The kit also has `academy` (url, name, environment) and `you` (the signed-in person's name, email, roles): say
    which Academy you are connected to and act as `you`."""
    return _client().kit()


@mcp.tool()
@_errors
def academy_validate(course: dict | str) -> dict:
    """Check a course against the schema without saving. `course` is the course JSON object or a path to a .json
    file. Returns issues with path and message; fix them and validate again before saving a draft."""
    c = _course(course)
    return _client().validate(c)


@mcp.tool()
@_errors
def academy_validate_brief(brief: dict | str) -> dict:
    """Check a course brief against the brief schema without saving it. `brief` is the brief JSON object or a path
    to a .json file. Checks the shape (every field, with its origin) and the rules: a safety-critical brief says
    whether the expert has seen it, a pass mark when there is a final test, a real case for safety_skill and
    awareness courses, a publisher who is not the author, https-only source links, and a course type that is a
    known recipe. Returns {ok, errors, warnings}, each issue with path and message."""
    return _client().validate_brief(_course(brief))


@mcp.tool()
@_errors
def academy_upload_media(path: str, provenance: str | None = None) -> dict:
    """Upload a file from this Mac to the Academy. Allowed: images (png, jpg, jpeg, webp, gif; max 10 MB), video
    (mp4; max 400 MB), iPhone HEIC/HEIF photos (max 25 MB) and MOV videos (max 400 MB), which are accepted and
    converted to JPEG and MP4 on upload (use the returned src), audio (m4a, mp3; max 50 MB) and captions (vtt; max 1 MB). Returns {src, sha256, ...}: put
    `src` in the course JSON. Images REQUIRE `provenance`: photo or screenshot (a real picture) or drawn or
    generated (made up). Say it honestly: the validator blocks drawn/generated images wherever a learner must
    recognise or copy something. Do this before validating and saving the draft."""
    return _client().upload_media(path, provenance)


@mcp.tool()
@_errors
def academy_request_render(spec: dict | str) -> dict:
    """Ask the Academy's render worker to make media. `spec` is a dict or a path to a .json file. Returns
    {job_id, status}; poll with academy_get_render. Kinds:
    - image: {"kind":"image","html":"<svg ...>","size":[1600,900],"alt":{"en","es"}} renders SVG/HTML to a PNG.
    - narration: {"kind":"narration","sections":[{"id":"s1","say":{"en","es"}}]} makes voice-over audio per section.
    - video: {"kind":"video","style":"walkthrough|photo_story|explainer","size":[1920,1080],"music":
      "calm|upbeat|none","title":{"en","es"},"scenes":[{"visual":{"src":"/media/<sha>.png"} or
      {"html":"<svg>","animate":false},"focus":[x,y,w,h] (percent),"say":{"en","es"},"minSeconds":3}]} makes a
      voiced EN+ES clip (max 300 s per language, max 60 scenes).
    See the kit's block catalog (academy_kit) for the full schema and caps.
    IMAGERY RULE (copy test): if a learner could copy or recognise anything in the picture (equipment, labels,
    PPE, screens), use a real photo or screenshot (upload it, then use its src in a scene). Drawn images are only
    for concepts, and must contain no words (text goes in the course, in both languages).
    Renders run on the Academy's render worker, so a job may report status waiting_for_worker until someone starts
    it. The finished job's `outputs` paste into the course JSON: image `media` as an image's media; narration
    `sections[].narrationAudio` into the section with the same id (`seconds` is for pacing only); video `block` (it
    has an id) into a section's blocks. Errors: 422 = spec problems (fix and resubmit), 429 = too many unfinished jobs (wait)."""
    return _client().request_render(_spec(spec))


@mcp.tool()
@_errors
def academy_get_render(job_id: str) -> dict:
    """Check a render job: {job_id, kind, status (queued|running|done|failed|waiting_for_worker), progress,
    outputs, problems, created_at, finished_at}. When done, paste `outputs` straight into the course JSON. If it
    stays waiting_for_worker, ask the person running the Academy to start the render worker. If failed, read
    `problems`, fix the spec and request again."""
    return _client().get_render(job_id)


@mcp.tool()
@_errors
def academy_save_draft(course: dict | str, note: str | None = None, draft_id: str | None = None,
                       change: str | None = None) -> dict:
    """Save the course as a draft revision (validate first). `course` is the JSON object or a path to a .json file;
    `note` says what changed; pass `draft_id` to add a revision to an existing draft. For an update of a published
    course, `change` ("small" or "material", the author's choice) is stored on the draft; leave it out to keep the
    one already stored. Returns draft_id, revision, validation and preview_url: share the preview link with the
    author for review. Claude cannot publish: a person publishes from the Academy after review."""
    _change(change, required=False)
    c = _course(course)
    return _client().save_draft(c, note, draft_id, change)


@mcp.tool()
@_errors
def academy_get_course(course_id: str) -> dict:
    """Read one of your published courses: {course_id, version, content, published_at, open_draft_id}. `content`
    is the live course JSON, with its stored brief. If open_draft_id is set, you already have an unpublished draft
    for this course: continue that one (academy_get_draft) rather than starting another. Only the course owner (or
    an admin) can read it."""
    return _client().get_course(course_id)


@mcp.tool()
@_errors
def academy_start_update(course_id: str, change: str, note: str) -> dict:
    """Start updating one of your published courses: copies the live content (every id kept) into a new draft.
    Ask the author first what changes and why (`note`) and whether it is a small fix or a material change
    (`change`):
    - "small": wording, images, a typo. Publishing makes the next minor version (1.1 → 1.2); completions and
      certificates stay valid.
    - "material": the procedure, a number, a hazard or a rule changed. Publishing makes the next major version
      (1.2 → 2.0) and everyone must retake the course; earlier certificates are superseded.
    Returns {draft_id, revision, preview_url, change}. If you already have an unpublished draft for this course,
    it returns that draft instead of starting another (check its `change`; save with academy_save_draft and
    `change` to correct it). Then edit the content and save it with academy_save_draft and the draft_id.
    Claude cannot publish: a person publishes from the Academy after review."""
    _change(change)
    return _client().start_update(course_id, change, note)


@mcp.tool()
@_errors
def academy_get_draft(draft_id: str) -> dict:
    """Read one of your drafts: latest content, validation and reviewer comments. Use it to apply review comments
    and then save a new revision with the same draft_id."""
    return _client().get_draft(draft_id)


@mcp.tool()
@_errors
def academy_list_my_courses() -> dict:
    """List your drafts and your published courses."""
    return _client().list_courses()


@mcp.tool()
@_errors
def academy_mark_ready(draft_id: str) -> dict:
    """Mark a draft ready for review by the testers. Only the author's own decision: ask first. This does not
    publish; Claude cannot publish, a person does that in the Academy."""
    return _client().mark_ready(draft_id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
