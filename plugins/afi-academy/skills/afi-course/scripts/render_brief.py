# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render a course brief for approval: <root>/<slug>/brief.json -> brief.html.

CLI:
    uv run render_brief.py <slug>
Writes brief.html next to brief.json and prints {"path": "..."} on stdout; on
failure exits 1 with {"error": "..."} on stderr. The course folder root is the
one folder.py uses ($AFI_ACADEMY_HOME or ~/AFI Academy/).
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE_PATH = HERE.parent / "assets" / "brief-template.html"

CHIPS = {"said": ("said", "You said"), "inferred": ("inf", "Claude's guess"), "default": ("def", "Standard choice")}
COURSE_TYPES = {
    "sop_floor": ("Floor procedure", "Step-by-step on the floor, with real photos."),
    "bc_howto": ("Business Central how-to", "Screens and steps in Business Central."),
    "bc_release": ("Business Central release", "What changed and what to do about it."),
    "uat": ("User acceptance test", "Testers follow scripted scenarios and report results."),
    "safety_skill": ("Safety skill", "Real photos for every step, must-pass questions, the expert ticks each step in review."),
    "awareness": ("Awareness", "Short and story-led, to change what people notice and report."),
    "policy_ack": ("Policy acknowledgement", "Read the policy, answer a few questions, acknowledge."),
    "onboarding": ("Onboarding", "A welcome path for new starters."),
}
KIND_TAGS = {"photo": "Real photo", "official": "Official image", "drawn": "Drawn", "video": "Video",
             "voiceover": "Voice-over", "screenshot": "Screenshot", "jobaid": "Job aid"}


def _folder():
    spec = importlib.util.spec_from_file_location("afi_folder", HERE / "folder.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def esc(s) -> str:
    return html.escape(str(s), quote=True)


NEEDS = '<span class="pend">Needs your answer</span>'


def _f(b: dict, key: str):
    """An answered {value, origin} field, or None when absent or null."""
    f = b.get(key)
    return f if isinstance(f, dict) and f.get("value") is not None else None


def _val(b: dict, key: str):
    f = _f(b, key)
    return f["value"] if f else None


def _list(b: dict, key: str) -> list:
    v = b.get(key)
    return v if isinstance(v, list) else []


def _safety(b: dict) -> bool:
    return bool(_val(b, "safetyCritical"))


def _date(iso: str | None) -> str:
    try:
        d = datetime.fromisoformat(iso).date() if iso else date.today()
    except ValueError:
        d = date.today()
    return f"{d.day} {d:%b %Y}"


def chip(origin: str | None, asked: bool = False) -> str:
    if origin is None:
        return ""
    cls, label = CHIPS.get(origin, CHIPS["default"])
    return f'<span class="chip {cls}{" asked" if asked else ""}">{esc(label)}</span>'


def field(label: str, dd: str, origin: str | None, asked: bool = False, why: str | None = None) -> str:
    w = f'<span class="why">{esc(why)}</span>' if why else ""
    return f'        <div class="f"><dt>{esc(label)}</dt><dd>{dd}{w}</dd>{chip(origin, asked)}</div>'


def needs_row(label: str) -> str:
    return f'        <div class="f"><dt>{esc(label)}</dt><dd>{NEEDS}</dd></div>'


def txt_field(b: dict, key: str, label: str, asked: bool = False, dd: str | None = None, need: bool = False) -> str:
    """One row for a Txt field. Absent: a "Needs your answer" row if `need`, else nothing."""
    f = _f(b, key)
    if not f:
        return needs_row(label) if need else ""
    return field(label, dd if dd is not None else esc(f["value"]), f.get("origin"), asked)


def section(sid: str, title: str, small: str, body: str) -> str:
    return (f'    <section class="sec" aria-labelledby="s-{sid}">\n'
            f'      <div class="sec-head"><h2 id="s-{sid}">{esc(title)}</h2><small>{esc(small)}</small></div>\n'
            f'{body}\n    </section>')


def fields(*rows: str) -> str:
    return '      <dl class="fields">\n' + "\n".join(r for r in rows if r) + "\n      </dl>"


def sub(label: str, origin: str | None) -> str:
    return f'      <div class="sub"><span>{esc(label)}</span>{chip(origin)}</div>'


def sec_purpose(b: dict) -> str:
    case_asked = _val(b, "courseType") in ("safety_skill", "awareness")
    g = _f(b, "goal")
    rows = fields(
        field("Goal", f'<p class="goal">{esc(g["value"])}</p>', g.get("origin")) if g else needs_row("Goal"),
        txt_field(b, "whyNow", "Why now", need=True),
        txt_field(b, "wrongToday", "What goes wrong today", need=True),
        txt_field(b, "realCase", "One real case", asked=case_asked, need=case_asked),
        txt_field(b, "supervisorCheck", "How a supervisor will know", need=True),
    )
    outcomes = _list(b, "outcomes")
    if outcomes:
        trs = "\n".join(
            f'            <tr><td><b class="o">{esc(o.get("id", ""))}</b> {esc(o.get("text", ""))}</td>'
            f'<td>{esc(o.get("practisedIn", ""))}</td><td>{esc(o.get("testedBy", ""))}</td></tr>'
            for o in outcomes)
        table = ('      <div class="tbl">\n        <table class="map">\n'
                 '          <thead><tr><th>Outcome</th><th>Practised in</th><th>Tested by</th></tr></thead>\n'
                 f'          <tbody>\n{trs}\n          </tbody>\n        </table>\n      </div>')
        tail = [sub("After the course, learners can", b.get("outcomesOrigin")), table]
    else:
        tail = [fields(needs_row("After the course, learners can"))]
    return section("purpose", "Purpose", "What the course is for", "\n".join([rows, *tail]))


def sec_class(b: dict) -> str:
    ct = _f(b, "courseType")
    if ct:
        label, why = COURSE_TYPES.get(ct["value"], (ct["value"], None))
        dd = f'{esc(label)} <code>{esc(ct["value"])}</code>'
        if why:
            dd += f'<span class="why">{esc(why)}</span>'
        ct_row = field("Course type", dd, ct.get("origin"))
    else:
        ct_row = needs_row("Course type")
    sc = _f(b, "safetyCritical")
    sc_row = (field("Safety-critical", "Yes" if sc["value"] else "No", sc.get("origin"), asked=True)
              if sc else needs_row("Safety-critical"))
    return section("class", "Topic and type", "Sets the defaults", fields(
        txt_field(b, "topic", "Topic", need=True),
        txt_field(b, "area", "Area and department", need=True),
        ct_row,
        sc_row,
    ))


def sec_audience(b: dict) -> str:
    return section("aud", "Audience", "Who takes it, and where", fields(
        txt_field(b, "who", "Who", need=True),
        txt_field(b, "languageFirst", "Language first", need=True),
        txt_field(b, "readingLevel", "Reading level", need=True),
        txt_field(b, "device", "Device", need=True),
        txt_field(b, "otherLanguages", "Other languages"),
        txt_field(b, "priorKnowledge", "Already knows", need=True),
    ))


def _source_row(s: dict) -> str:
    title = esc(s.get("title", ""))
    excerpt = s.get("excerpt")
    url = s.get("url")
    if url and url.startswith("https://"):
        title = f'<a href="{esc(url)}" rel="noopener noreferrer">{title}</a>'
    if excerpt:
        title += f'<span class="why">\u201c{esc(excerpt)}\u201d</span>'
    role = ('<span class="auth">Authoritative</span>' if s.get("role") == "authoritative"
            else '<span class="bg">Background</span>')
    return (f'            <tr><td>{title}</td><td>{role}</td><td>{esc(s.get("asOf") or "")}</td>'
            f'<td>{esc(s.get("use", ""))}</td><td>{esc(s.get("rights", ""))}</td></tr>')


def sec_sources(b: dict) -> str:
    sources = _list(b, "sources")
    if sources:
        trs = "\n".join(_source_row(s) for s in sources)
        table = ('      <div class="tbl">\n        <table>\n'
                 '          <thead><tr><th>Source</th><th>Role</th><th>As of</th><th>Use</th><th>Rights</th></tr></thead>\n'
                 f'          <tbody>\n{trs}\n          </tbody>\n        </table>\n      </div>')
    else:
        table = fields(needs_row("Sources"))
    seen = _f(b, "expertSeenBrief")
    seen_row = ""
    if seen:
        if seen["value"] == "yes":
            dd, why = "Yes", None
        else:
            dd, why = '<span class="pend">Not yet</span>', "You can approve without it. It shows on the hand-over too."
        w = f'<span class="why">{esc(why)}</span>' if why else ""
        seen_row = (f'        <div class="f"><dt>Expert has seen this brief</dt><dd>{dd}{w}</dd>'
                    f'{chip(seen.get("origin"), asked=_safety(b))}</div>')
    elif _safety(b):
        seen_row = needs_row("Expert has seen this brief")
    auth = ", ".join(esc(x.get("title", "")) for x in sources if x.get("role") == "authoritative")
    auth_row = field("Authoritative sources", auth, "said", asked=True) if auth else needs_row("Authoritative sources")
    return section("src", "Sources", "Where every fact comes from", "\n".join([
        table, fields(auth_row, txt_field(b, "expert", "Expert of record", asked=True, need=True), seen_row)]))


def _kind(k: dict) -> str:
    return (f'        <div class="kind"><span class="tag">{esc(KIND_TAGS.get(k["kind"], k["kind"]))}</span>'
            f'<b>{esc(k["title"])}</b><span>{esc(k["note"])}</span></div>')


def sec_format(b: dict) -> str:
    lessons = b.get("lessons")
    if lessons:
        lesson_row = field("Lessons", " &nbsp; ".join(f"{i} · {esc(t)}" for i, t in enumerate(lessons, 1)),
                           b.get("lessonsOrigin"))
    else:
        lesson_row = needs_row("Lessons") if lessons is None else ""
    parts = [fields(txt_field(b, "length", "Length", need=True), lesson_row, txt_field(b, "jobAid", "Job aid"))]
    kinds = b.get("contentKinds")
    if kinds:
        parts.append(sub("Kinds of content", b.get("contentOrigin")))
        parts.append('      <div class="kinds">\n' + "\n".join(_kind(k) for k in kinds) + "\n      </div>")
    elif kinds is None:
        parts.append(fields(needs_row("Kinds of content")))
    return section("fmt", "Format", "How it is presented", "\n".join(parts))


def sec_test(b: dict) -> str:
    safety = _safety(b)
    has_test = _f(b, "finalTest") is not None
    pm = _f(b, "passMark")
    if pm:
        pm_row = field("Pass mark", f'{esc(pm["value"])}%', pm.get("origin"), asked=True)
    else:
        pm_row = needs_row("Pass mark") if has_test else ""
    return section("test", "Assessment", "How we know it worked", fields(
        txt_field(b, "practice", "Practice", need=True),
        txt_field(b, "finalTest", "Final test"),
        txt_field(b, "difficulty", "Difficulty"),
        pm_row,
        txt_field(b, "mustPass", "Must-pass questions", asked=True, need=has_test),
        txt_field(b, "handsOn", "Hands-on sign-off", asked=safety, need=True),
        txt_field(b, "acknowledgement", "Acknowledgement"),
    ))


def sec_after(b: dict) -> str:
    return section("after", "After launch", "Review and renewal", fields(
        txt_field(b, "certificate", "Certificate", need=True),
        txt_field(b, "reviewers", "Reviewers", need=True),
        txt_field(b, "publisher", "Publishes", need=True),
        txt_field(b, "pilotRun", "Pilot run"),
        txt_field(b, "readyBy", "Ready by", need=True),
        txt_field(b, "reviewAgain", "Review again", need=True),
        txt_field(b, "updateOwner", "Update trigger owner", need=True),
    ))


def open_items(b: dict) -> str:
    needs = b.get("stillNeeded") or []
    if not needs:
        return ""
    lis = "\n".join(f'        <li><span>{esc(n.get("text", ""))}</span><em>{esc(n.get("who", ""))}</em></li>' for n in needs)
    return (f'    <section class="open" aria-labelledby="s-open">\n      <h2 id="s-open">Still needed</h2>\n'
            f'      <ul>\n{lis}\n      </ul>\n    </section>')


def limits(b: dict) -> str:
    items = b.get("limits")
    head = f'<h3 id="s-limit">{esc("What this course can't do on its own")}</h3>'
    if items is None and _safety(b):  # always asked for a safety-critical course
        body = f'      <p>{NEEDS}</p>'
    elif items:
        body = "      <ul>\n" + "\n".join(f"        <li>{esc(x)}</li>" for x in items) + "\n      </ul>"
    else:
        return ""
    if _safety(b):
        head = ('<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">'
                f'{head}{chip("said", asked=True)}</div>')
    return f'    <section class="limit" aria-labelledby="s-limit">\n      {head}\n{body}\n    </section>'


def is_approved(b: dict) -> bool:
    return b.get("version") is not None and b.get("approvedVersion") == b["version"]


def state_label(b: dict, open_answers: bool = False) -> str:
    if open_answers:
        return "Waiting for your answers"
    if is_approved(b):
        return f'Approved v{b["version"]}'
    return "Waiting for your approval"


def meta(b: dict) -> str:
    approved = is_approved(b)
    when = _date(b.get("approvedAt")) if approved and b.get("approvedAt") else _date(None)
    expert = _val(b, "expert") or ""
    if len(expert) > 60:  # keep the lead phrase; "Dr. Smith, EHS" stays whole
        i = expert.find(". ", 15)
        expert = expert[:i] if i > 0 else expert
    v = b.get("version")
    author = esc(b["author"]) if b.get("author") else NEEDS
    spans = [f'<span>Brief <b>v{esc(v) if v is not None else "?"}</b> · {esc(when)}</span>',
             f"<span>Author <b>{author}</b></span>",
             f"<span>Expert of record <b>{esc(expert) if expert else NEEDS}</b></span>"]
    if approved and b.get("approvedAt"):
        spans.append(f'<span>Approved <b>{esc(_date(b["approvedAt"]))}</b></span>')
    if b.get("change"):
        note = f' · {esc(b["changeNote"])}' if b.get("changeNote") else ""
        spans.append(f'<span>Change <b>{esc(str(b["change"]).capitalize())}</b>{note}</span>')
    spans.append("<span>Built with <b>/afi-course</b></span>")
    return "\n      ".join(spans)


def glance(b: dict) -> str:
    def v(x) -> str:
        return esc(x) if x else "—"

    lang = " · ".join(x for x in (_val(b, "languageFirst"), _val(b, "readingLevel")) if x)
    test = [x for x in (_val(b, "finalTest"),) if x]
    if _f(b, "passMark"):
        test.append(f'pass {b["passMark"]["value"]}%')
    rows = [("Length", v(_val(b, "length"))), ("For", v(_val(b, "who"))), ("Language", v(lang)),
            ("Device", v(_val(b, "device"))), ("Test", v(" · ".join(test))), ("Certificate", v(_val(b, "certificate")))]
    sc = _f(b, "safetyCritical")
    if not sc:
        rows.append(("Safety", "—"))
    elif sc["value"]:
        rows.append(("Safety", '<span class="safety">Safety-critical</span>'))
    seen = _val(b, "expertSeenBrief")
    if seen:
        rows.append(("Expert", "Has seen the brief" if seen == "yes" else "Hasn't seen the brief yet"))
    elif _safety(b):
        rows.append(("Expert", "—"))
    return "\n".join(f"        <div><dt>{esc(k)}</dt><dd>{x}</dd></div>" for k, x in rows)


def _title(b: dict) -> dict:
    t = b.get("title")
    return t if isinstance(t, dict) else {}


def footer(b: dict) -> str:
    note = "approved" if is_approved(b) else "saved with the course draft once approved"
    v = b.get("version")
    left = f'{esc(_title(b).get("en") or "Course brief")} · brief v{esc(v) if v is not None else "?"} · {note}'
    url = b.get("artifactUrl")
    if url and str(url).startswith("https://"):
        u = esc(url)
        left += f' · <a href="{u}" rel="noopener noreferrer">{u}</a>'
    return f"<span>{left}</span><span>AFI Academy</span>"


def render(brief: dict, template: str) -> str:
    """Render any brief, however incomplete: an unanswered field shows a "Needs your answer" badge."""
    t = _title(brief)
    sections = "\n\n".join([sec_purpose(brief), sec_class(brief), sec_audience(brief), sec_sources(brief),
                            sec_format(brief), sec_test(brief), sec_after(brief)])
    slots = {
        "TITLE_TEXT": esc(t.get("en") or "Course"),
        "TITLE": esc(t["en"]) if t.get("en") else NEEDS,
        "TITLE_ES": esc(t.get("es") or ""),
        "META": meta(brief),
        "SECTIONS": sections,
        "OPEN": open_items(brief),
        "LIMITS": limits(brief),
        "GLANCE": glance(brief),
        "FOOTER": footer(brief),
    }
    open_answers = (any(NEEDS in slots[k] for k in ("TITLE", "META", "SECTIONS", "LIMITS"))
                    or any(str(n.get("text", "")).startswith("Needs your answer")
                           for n in _list(brief, "stillNeeded") if isinstance(n, dict)))
    slots["STATE"] = esc(state_label(brief, open_answers))
    # One pass, so a "{{X}}" typed by the author is never expanded.
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: slots.get(m.group(1), m.group(0)), template)


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ns = ap.parse_args(argv)
    try:
        d = _folder()._dir(ns.slug)  # validates the slug
        src = d / "brief.json"
        if not src.is_file():
            raise ValueError(f"no brief.json for course: {ns.slug}")
        out = d / "brief.html"
        out.write_text(render(json.loads(src.read_text(encoding="utf-8")),
                              TEMPLATE_PATH.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    except (ValueError, TypeError, KeyError, OSError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"path": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
