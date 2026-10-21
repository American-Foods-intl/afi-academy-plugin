# Write, save and hand over

Goal: one bilingual draft in the AFI Academy, written from the approved brief and the course folder, every fact
traced to a source, and a hand-over that tells the author exactly what's left. **Every content rule (format, rhythm,
writing, Spanish, pictures, quizzes, citation format, placeholders, render specs) is in the kit's writing guide and
block catalog (`academy_kit`).** Follow them; this file only says what to do in which order.

The course file is `<root>/<slug>/course.json` (`folder.py root`). Order of work:

| Step | What | Where |
|---|---|---|
| 1 | Check the folder; pull the Academy draft if there is one | § 1 |
| 2 | Write the course in one pass, EN and ES | § 2 |
| 3 | Media: upload, render, keep pending jobs | § 3 |
| 4 | Trace check | § 4 |
| 5 | Validate until there are no errors | § 5 |
| 6 | Rubric: score, fix the two weakest lines, Spanish register check, validate until no errors | `self-check.md` § 1 |
| 7 | Save the draft | § 6 |
| 8 | Look at the preview, fix, save a new revision | `self-check.md` § 2 |
| 9 | Hand over | § 7 |

## 1. Before any write

0. **An update** (`state.json` has `update_of` or `change`): don't write the whole course. Follow `update.md` § 5 (change only
   what the change note says); it sends you to § 3–7 here for media, tracing, validation, saving and the hand-over.
1. **The brief is approved and current:** `brief.json` `approvedVersion` equals its `version`, and equals `state.json`
   `approved_version`. If not, stop: show the version and go back to `brief-fields.md` § Approval.
2. **Nothing is open:** `folder.py open-needs` returns `[]`. If not, go back to `gather.md`.
3. **The Academy draft is the master once it exists.** If `state.json` has a `draft_id`, call `academy_get_draft` with
   it **before you change `course.json`**, write its `content` to `course.json` (replacing the local file) and record
   its `revision` with `set-state`. Then make your changes on that. Never save a local copy over a newer revision. If
   the draft has reviewer comments, say so and follow the review loop (`review-loop.md`) instead.
4. **A write already started:** if `course.json` exists and there is no `draft_id` (an earlier session stopped
   before the first save), continue from `course.json`. Don't start over, and don't drop what it already has.
5. `set-state` with `"phase": "write"`.
6. **Tell the author it takes a while**, in one line, before you start: "Writing the course now, in English and
   Spanish. This takes a few minutes."

## 2. Write the course: one pass, EN and ES

Read first: the kit's writing guide, block catalog and example course; the course type file's **Structure**; the
approved `brief.json`; `needs.json` (the notes hold the gathered answers); `assets.json`; `log.md`.

Write the whole course in one pass, English and Spanish together, every text in both. Don't write one language and
translate later. Take these values from the brief:

| Course | From the brief |
|---|---|
| `id` | the folder slug (or `state.json` `course_id`, if a save changed it: § 6) |
| `recipe` | `courseType` |
| `title` | `title` |
| `safetyCritical` | `safetyCritical` |
| `lessons` | `lessons`, in that order (sections planned on the recipe in the kit's writing guide) |
| `minutes` | `length` |
| `assessment` | `finalTest` (pool, draw, attempts), `passMark`; `mustPass` items get `critical: true` |
| `certificate` | `certificate` |
| `reviewBy` | `reviewAgain` |
| `owner` | the author (`academy_kit`'s `you`) |
| `brief` | the whole `brief.json`, copied as it is |
| `sources` | one per brief source: same `id` and `title`; `authoritative` = `role` is `authoritative`; `url`, `asOf` and `excerpt` copied when the brief has them. Sources added in gather follow. |

**Every fact comes from a source or the needs list.** A step, number, location, product, PPE item or rule is either in
an authoritative source you read, or in a done need's note. A fact a person gave in gather (not from a document) gets
its own course source, for example `{"id": "S5", "title": "Facilities manager, answer of 3 Nov 2026 (where the
ladders are stored)", "authoritative": false}`, and goes on the expert's list in the hand-over. A waived fact is
written as visible "TO CONFIRM" text, as the kit says. Anything else you'd need: stop and go back to `gather.md`; never invent it.

The real case (`realCase`) drives the story and the scenario. The top mistakes (`wrongToday`) drive the compare blocks
and the wrong options.

Write the file with your file tool to `course.json`, and log "course written from brief v<N>".

## 3. Media

**Every entry in the approved brief's `contentKinds` gets made in this pass:** `drawn` → an `image` render request,
`voiceover` → a `narration` render request, `video` → a `video` render request, and real media (`photo`, `official`,
`screenshot`) → an upload (or a waived placeholder). A native block (for example a process flow) may be used in
addition, never instead of the render. If one can't be made, say so in the hand-over with the reason.

- **Real files** (photos, official images, screenshots, video) from `assets/`: for each file the course uses whose
  `assets.json` `src` is `null`, call `academy_upload_media` with its full path and the provenance recorded in
  `assets.json`, then `folder.py set-asset-src`. Never upload twice: reuse a recorded `src`. Never upload or use a file whose
  notes start with `rejected:`. Put the returned `src` in
  the course as it is, with the same provenance.
- **A waived photo** is a `placeholder` image with the need's shot description, never with "TO CONFIRM" in it (that
  marks only an unconfirmed fact; the placeholder already marks the photo).
- **Drawn images** (concepts only, as the kit's imagery rule allows): `academy_request_render` kind `image`, in the
  house style (`house-style.md`).
- **Voice-over:** kind `narration`, when the brief's content kinds include it. **Video:** kind `video`, from uploaded
  real photos or drawn scenes, when the brief asks for one.
- **Every render job id goes into `state.json` straight away:** `set-state` with `"pending_renders": [{"job_id": …,
  "kind": …, "for": "<where the output goes: section id, block id or media path>"}, …]` (the whole list each time).
- Poll `academy_get_render`. When a job is `done`, paste its `outputs` into the course exactly as the kit's block
  catalog says (Render tools), then remove the job from `pending_renders` (when there is a `draft_id`: only after the
  save that contains it succeeds). `failed`: read `problems`, fix the spec,
  request again. `waiting_for_worker`: keep the job id and its `for`, and leave that piece out of the course (no
  video block, no `narrationAudio`, no image media): never invent a `/media/` path. Write and save everything else (a
  section's narration with no audio is only a warning), and tell the author it finishes when the render worker runs.
  Describe only what the saved course contains: a piece left out is named as still coming, never as there or as
  replaced by something you didn't write.
- **Before you wait on renders**, say so in one line ("Making the voice and the illustration now. This takes a few
  minutes."). **When they finish**, say what was made in one line: "Done: the voice for 9 screens, in English and
  Spanish, and one illustration."
- **On a later session** (the continue route), call `academy_get_render` for each job in `pending_renders` first, paste
  the finished outputs (pull the draft first, § 1), validate and save a new revision.

## 4. Trace check (before the first save)

Go through the course and fix every gap:

- **Outcomes:** every brief outcome has practice (`check` blocks, or a scenario plus a check) in the lessons, before
  the final test, and every practice and final-test question carries the outcome it serves as `objective` (the brief's
  outcome id, for example `O1`). Every outcome has at least one final-test item when there is a test.
- **No fact without a source:** every procedure step, number, key fact, danger callout and quiz item carries a
  `source`, in the kit's citation format (`"<source id>"` or `"<source id> <locator>"`, for example `"S1 (l)(1)"`), and
  the id is in the course `sources`. A number in running text sits next to a cited block that states it.
- **Placeholders match waivers:** every `placeholder` and every "TO CONFIRM" corresponds to a **waived** need in
  `needs.json`, and every waived need appears as one. A placeholder with no waiver means a fact or a photo went
  missing: go back to `gather.md`.
- `brief` is in the course and equals `brief.json`; `sources` carry the brief's `url`, `asOf` and `excerpt`.

## 5. Validate

Call `academy_validate` with the path of `course.json`. Fix every error and validate again, until there are **no
errors**. Then fix every warning you can. The warnings that may stay: placeholders and "TO CONFIRM" for waived needs,
and "voice-over pending" for narration still rendering. Never remove a placeholder or a citation to make a warning go
away.

Then run the rubric (`self-check.md` § 1). After its fixes, validate once more until there are no errors, and
save (§ 6).

## 6. Save

1. If there is a `draft_id`: `academy_get_draft` first. If its `revision` is newer than the one you pulled, someone
   changed it meanwhile: pull it (§ 1, step 3) and make your changes again on it. Validate again: no errors.
   **Then its `status`:**
   - `published`: don't save. The course went live from this draft, so a change is now an update: tell the author in
     one line and take the update route (`update.md`; a folder with `update_of`: § 1 step 6).
   - `in_review`: save. Then, in your closing reply (SKILL.md: questions come last), one plain line: "Saving this
     took the draft out of review: reviewers won't see it until it's marked ready again", and ask "Do you want me to
     mark it ready for review again?" Mark it only on their own words (`review-loop.md` § 5).
   - Anything else: save.
2. `academy_save_draft` with the path of `course.json`, a `note` (what this revision is: "First draft from brief v1,
   ladder-rack photo still a placeholder"), and the `draft_id` when `state.json` has one.
   On an update draft (`state.json` has `change`), also pass `change` with that value, every time (`update.md`).
3. On success: `set-state` with `"draft_id"`, `"revision"` and `"phase": "saved"`; log the revision and the
   `preview_url`. Check the returned `validation`: errors there are fixed and saved again.
4. **The id belongs to someone else** (error `course_owned_by_other`, status 403): another person owns a course with
   this id, and that can't be seen before the first save. Run `folder.py suggest-slug --json '{"title": "<current id>",
   "taken": [<current id>, the local slugs, every `academy_list_my_courses` id]}'`, tell the author in one line
   ("Another course already uses the id `ladder-safety-repack`, so this one will be `ladder-safety-repack-2`."), set
   the course `id` to the new one in `course.json`, record it with `set-state` `"course_id": "<new id>"` (the folder keeps its name), log it, and save
   again **once**. If that fails too, stop and tell the author what the Academy said.

Then look at the preview (`self-check.md` § 2).

## 7. Hand over

One message to the author, **at most about 15 short lines**, in plain words (SKILL.md § Talking to the author: no ids,
scores or percentages), in this order:

1. **The preview link** (`preview_url`), and in the same line that it's a draft: reviewers comment in the Academy, a
   person other than the author publishes, and it isn't live.
2. **What the course covers**, in 2–3 lines: the lessons and the minutes, the test (pass mark, must-pass questions)
   or the acknowledgement.
3. **What's still needed, and from whom**: each placeholder by its plain name, grouped by who supplies it ("Please
   ask Dana: …"), and, on a safety-critical course, that they must be replaced before it can be published. Then the
   brief's process items (`gather.md` § 1, for example someone to check the Spanish), with who does each.
4. **What the expert must check**, named, grouped by where it came from, a line each: from the rule, from AFI's
   document, from answers given in chat, and every "TO CONFIRM". Add whether the expert has seen the brief ("not yet"
   / "yes"; "no expert: your decision" when the expert is "None (author's decision)").
5. **The two weakest points**, one plain line each (`self-check.md` § 1).
6. **Voice, video and illustrations**: what was made, or what is still being made and finishes on its own, and any
   media kind from the brief that couldn't be made, with the reason (one line).
7. **If you couldn't look at the preview**, one line: "I couldn't look at the preview myself (the Academy's checks found
   no errors). Please open the link on your phone, switch to Spanish, and check that no text is cut off."
   (`self-check.md` § 2).
8. What's next, one line: "When the reviewers have commented, say 'address the review on the <title> course'." Mark
   it ready for review (`academy_mark_ready`) only if the author asks in their own words.

The full step-by-step list for the expert (every procedure step, number and danger callout with its source) goes in
the log (`folder.py log`), not in the message. Log "handed over revision <N>".
