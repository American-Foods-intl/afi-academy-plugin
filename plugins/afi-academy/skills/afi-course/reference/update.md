# Update a published course

Goal: change a published course with a **change note**, not a new brief, unless the change touches the brief's scope.
The result is an update draft in the Academy, ready for review. **What publishing does is decided only by the `change`
you pass to the Academy** (`small` or `material`, the author's answer): always pass it to `academy_start_update`, and
to every `academy_save_draft` on the update draft. The brief's `change` is a record of it, never relied on.

The course id is `state.json` `course_id` when it is set, otherwise the folder slug. **An update in progress** is a
folder whose `state.json` has `update_of` (the course id), set in § 1 step 4 as soon as the update starts, with
`update_started_version` (the published version then) and, once the author answers § 2, `change`. The three stay
until the update is published. A later session resumes it with § 1.6 (SKILL.md § Continue); it never goes through
`write.md`'s one-pass write.

## 1. Load the course and its stored brief

1. **Find it:** `academy_list_my_courses`, and the local folder whose slug or `course_id` (`folder.py get-state`)
   matches.
2. `academy_get_course` with the course id. It returns `content` (the live course, with its stored brief under
   `brief`, when there is one), `version` and `open_draft_id`. **Not found** (the course was never published): it
   isn't an update. Its saved draft is changed with `review-loop.md` § 6 (SKILL.md, route **change the draft**).
3. **An update is already open** (`open_draft_id` set): `academy_get_draft` on it and tell the author (its `change`,
   revision and comments). Comments: follow `review-loop.md`. Otherwise ask whether to carry on with it; a second
   update draft can't be started. Carrying on: its `change` is checked in § 5 step 2.
4. **The folder.** If its `state.json` already has `update_of`, resume instead (step 6). No local folder:
   `folder.py init-course` with the course id as the slug and the English title, write the stored brief to
   `brief.json`, and `set-state` with `"brief_version"` and `"approved_version"` = its `approvedVersion`. A folder that
   exists: the stored brief is the one that was published; if `brief.json` differs, use the stored one and say so.
   **Always remove `change` and `changeNote` from `brief.json` here**, rewritten or not: they belong to the last
   update (§ 5 step 4 records the new ones). **No stored brief:** build `brief.json` from the course content, every
   field `inferred`, at `version` 1 with no approval (`approved_version` stays empty), and run
   `academy_validate_brief` on it; the change note's go-ahead covers the update.
   Then mark the update as started: `set-state` with `"update_of": "<course id>"` and `"update_started_version":
   "<version>"` (from step 2).
5. **Show what you loaded** in two lines: the title and published version, the type, who takes it, the expert. The
   stored brief's answers stand (expert, sources, pass mark, must-pass questions, …): don't ask them again unless the
   change touches them. A brief you built (step 4): show what you read and ask the author to confirm each always-asked
   answer, as for a spin-off (`intake.md` § 4); a confirmed answer becomes `said`. Ask also for what the content
   can't give and the validation asks for (for example the publisher, a real case), with the always-asked rules
   (`intake.md` § 3), then validate again.
6. **Resuming** (`state.json` has `update_of`), the one rule: `academy_get_course` with it. If `pending_renders` isn't
   empty, first collect the finished ones (SKILL.md § Continue, step 2).
   - `open_draft_id` set: that is the update draft. `academy_get_draft` on it: open reviewer comments, or the author
     says "address the review" → `review-loop.md`. Phase `saved` or `review`: the author asks for a change in their
     own words → `review-loop.md` § 6 (with `change` on every save); nothing asked yet → show its state in a few
     lines (the change note, the revision, its review status) and ask what the author wants: change something in
     this update, or nothing. This step owns an open update draft: never send it back to **continue (saved)** or to
     the start of this file. Any other phase → § 5 step 2.
   - No open draft, and `version` differs from `update_started_version`: the update was published. Tell the author,
     clear the markers (`set-state` with `"update_of": null`, `"update_started_version": null`, `"change": null`),
     remove `change` and `changeNote` from `brief.json`, log it, and start again at step 1 if they want another change.
   - No open draft, same `version`: nothing was started in the Academy yet, so no go-ahead was acted on. Pick up where
     it stopped: no `change` yet → § 2; a full brief started but not approved (`brief.json` has `change`, and
     `approvedVersion` ≠ `version`) → § 6; a full brief approved (`brief.json` has `change`, and `approvedVersion` =
     `version`) → § 4; otherwise → § 3 (does the change touch the scope?), then § 4 (the change note, the go-ahead)
     and § 5 from step 1.

## 2. Ask what changes, and whether people retake it

One round:

- **"What changes, and why?"** Free text: restate it in one line.
- **"Where does the new information come from?"** A document (save it in `assets/` and record it, `gather.md` § 3) or
  a person, by name. House rule 5 applies to every new step, number or fact.
- **"Does everyone who already passed need to take it again?"** Before they choose, say what each answer does:
  - **No: a small fix** (wording, a picture, a typo, a detail that doesn't change what people do). Publishing makes the
    next minor version (1.1 → 1.2); completions and certificates stay valid.
  - **Yes: a material change** (a step, a number, a hazard or a rule changed). Publishing makes a new required version
    (1.2 → 2.0): everyone's certificate for this course is superseded and everyone must take it again, with their
    group's full time to do it (a grace period).

  It is the author's choice: never infer it. "You decide": propose one answer with a one-line reason as a yes/no
  question (`intake.md` § Question rounds); without a yes, nothing is started. If they pick small for a change to a
  step, number, hazard or rule, say once that this usually means everyone retakes; their answer stands. Record the
  answer: `set-state` with `"change": "<small|material>"`.

## 3. Does it touch the scope?

The scope is who takes it (`who`), what they must be able to do (`outcomes`) and the kind of course (`courseType`).

- **It doesn't:** say so in one line ("This doesn't change who takes it, what they must be able to do, or the kind of
  course, so a change note is enough.") and go to § 4.
- **It does:** say which, and offer the two ways (AskUserQuestion): a **full brief** for this course (§ 6), or a
  **spin-off** (§ 7) when the original should stay as it is for the people who take it now.

## 4. The change note, then the go-ahead

Show it in chat:

> **Change note: <course title>**
> - What changes: …
> - Why: …
> - Source: …
> - Small fix (nobody retakes) / Material change (a new required version: everyone retakes)

Then: "Reply **go ahead**, or tell me what to change." Only an explicit go-ahead counts (like an approval,
`brief-fields.md` § Approval, step 8). Then go straight to § 5: nothing is written locally before the pull.

## 5. After the go-ahead: open the draft, pull, record, gather, change, save

A later session resumes with § 1 step 6.

1. **Open the update draft:** `academy_start_update` with the course id, `change` (the author's answer) and `note`
   (the change note). Skip it when there is already an open draft (§ 1 step 3, or resuming).
2. **Check the declared change.** The draft's `change` (from `academy_start_update` or `academy_get_draft`) must equal
   the author's answer (`state.json` `change`). If they differ, tell the author both and ask which
   is right; never overwrite one with the other on your own. Their answer is the `change` for every save.
3. **Pull before you change anything:** `academy_get_draft` with the `draft_id`, and write its `content` to
   `course.json`.
4. **Record it:** in `brief.json`, `change` (the author's answer) and `changeNote` (one line: what, why, source); the
   brief's `version` and approval stay as they are (the change note is approved in chat, not a new brief). Put the
   same brief in `course.json` `brief`. `folder.py set-state` with `"draft_id"`, `"revision"`, `"change"` (the answer
   from step 2) and `"phase": "write"`; `folder.py log` the change note.
5. **Gather** what the change needs (`gather.md`): new facts with their source, new photos; wait or a placeholder as there.
   Run `set-needs` with the full list: the existing items plus the new ones (`gather.md` § 1). When nothing is open,
   come back here to step 6, not to `write.md`.
6. **Change only what the note says**, English and Spanish, every id kept: never rewrite the whole course. Then
   `write.md` § 3–5: media, the trace check on the changed blocks, validate until no errors.
7. **Save** (`write.md` § 6) with the `draft_id`, `change` = the author's answer, and a note ("Update, small fix: …").
   `set-state` with `"phase": "saved"`.
8. **Hand over** (`write.md` § 7), starting with the change note and what publishing will do (small: completions stay
   valid; material: everyone retakes, with a grace period). Mark it ready for review only when the author asks in
   their own words (`review-loop.md` § 5). Never publish, and never say the update is live.

## 6. A full brief instead (the scope changes)

Start from the stored brief: add 1 to `version`, keep every value and its origin, set `change` and `changeNote`.
Ask what changes in the scope, plus each always-asked question the change touches (`intake.md` § Question rounds).
Then `brief-fields.md` § Approval: validate, render, publish, and an explicit approval. Step 7 there records the
approval; then come back here instead of loading `gather.md`: § 2's retake question if it isn't answered yet, and
§ 5 from step 1 (gather happens inside § 5, step 5).

## 7. A spin-off instead (a new course alongside)

When the author wants the same course for other people, another site or another kind of course, and the original
stays: that is a new course, the spin-off route (`intake.md` § 4): a new slug and folder, a new brief at version 1
pre-filled from the original (every value `inferred`), the new goal and audience asked outright, every always-asked
question asked again, and a full approval. Never call `academy_start_update` for a spin-off: the original isn't
touched. If § 1 already marked the original's folder, clear its markers (`update_of`, `update_started_version`,
`change`: `null`). When it isn't clear, ask one question: "Should this replace the current course for everyone who
takes it, or be a separate course alongside it?"
