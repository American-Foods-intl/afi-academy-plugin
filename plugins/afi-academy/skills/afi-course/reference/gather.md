# Gather

Goal: before a word of the course is written, everything it needs that you can't source yourself is in the course
folder, or the author has asked for a placeholder for it in their own words (a waiver, in the files). Gather follows approval (`brief-fields.md` § Approval, step 7)
and is state phase `gather`. Writing starts only when `folder.py open-needs` returns `[]` (`write.md`).

The assets folder is `<root>/<slug>/assets/`, where `<root>` is what `folder.py root` prints. Whenever you ask for a
file, give the author this **full path** (for example `/Users/jordan/AFI Academy/ladder-safety-repack/assets/`), never just
"the folder".

## 1. Build the needs list

Go through the approved brief and list everything the course needs that you can't source yourself:

1. **The brief's "Still needed" items the content depends on** (a fact, a document, a photo or screenshot), one need
   each. Items about the process (someone to check the Spanish, an expert to confirm, a reviewer, a pilot run) are
   not needs and never hold up the writing: they go on the hand-over's "still needed" list (`write.md` § 7). Ask about
   them at most once after approval, in the § 2 round, with no wait-or-placeholder choice.
2. **Every procedural step and fact the sources don't cover.** Walk the lessons and outcomes: each step, number,
   location, contact, product or chemical, PPE item and local rule the course will state. If an authoritative source
   in the brief says it (and you read it), it isn't a need. If not, it is a `fact` need, from the person who knows (usually
   the expert of record or the author). Never fill one from memory, from another company or from a "typical" value.
3. **Photos and screenshots**, one need per shot, following the kit's imagery rule (writing guide, Pictures): every real
   thing the learner must recognise or copy. Official symbols (for example hazard pictograms or safety signs) are a need too: the official
   file from its source, never redrawn. Try to download it yourself; if you can't, the need goes to the author as
   "Please save <what> from <page> into <full assets path>" (SKILL.md § Talking to the author).
4. **Expert input**: open conflicts between sources (`log.md`), and any value only the expert can supply. The expert
   confirming the course as a whole is a process item (item 1), not a need.

Write it with `folder.py set-needs --json '{"slug": …, "items": [{"id": "n1", "text": …, "who": …, "kind": …}]}'`.
`kind` is `fact`, `photo`, `screenshot`, `expert` or `other`; `who` is a name or a role. If a need turns up later,
run `set-needs` again with the full list: items already in the list keep their status and note (answers and waivers
are kept), new ids start open, and ids you leave out are dropped.

### Shot descriptions

Every photo or screenshot need is written as a shot the author can take without asking you anything:

- **the subject**, at AFI (the 6-foot step ladder in the repack room, not "a ladder");
- **the framing**: wide (where am I), action (hands doing the step) or detail (the part filling the frame);
- **people**: no faces in a "wrong way" photo (hands only); correct PPE in a "right way" photo; anyone identifiable
  needs their consent on file;
- **nothing private**: no customer names, prices, personal data or badges; a screenshot from the real system, with
  personal data cropped or blurred.

Example: "Detail: the step ladder's spreader locked open, filling the frame. No people. Landscape."

## 2. Ask for it

Show the list grouped by **who supplies it**, each item by its plain name (never its id), the shot descriptions one
line each, and the full `assets/` path once. This is the one time photos and screenshots are asked for. Then:

- **Items from someone named:** "Please ask Dana: where are the ladders stored?" The author passes it on; you never
  address Dana.
- **Items with no one named yet:** ask "Who can take these photos?" or "Who can tell us …?", and record the answer
  as `who`. Never write the author in as the supplier unless they say they'll do it.
- **Process items** (§ 1): once, after the list, saying they don't hold up the writing ("Still to arrange: who will
  check the Spanish?"). Whatever the answer, writing goes ahead.
- **Questions:** at most 4 per round, AskUserQuestion for choices, plain text for facts.

Facts the author answers in chat: restate them in one line,
then `folder.py mark-need --json '{"slug": …, "id": "n3", "status": "done", "note": "<the answer, who said it, date>"}'`
and `folder.py log --json '{"slug": …, "line": "…"}'`. A fact from a document: save the document in `assets/`,
record it (§ 3), and put the document and
locator in the note.

## 3. Check every file

At the start of each gather turn, run `folder.py untracked-assets` to find files the author dropped in. For each file:

1. **Read it** (look at the image, read the document).
2. **Right subject?** Compare it with the need's shot description. Wrong subject, wrong framing, or a "right way" photo
   with unsafe practice in it: say what's wrong and ask for a retake. Don't use it.
3. **Personal data?** Faces anywhere in the frame (background, mirrors, glass), names, badges, screens with personal data,
   customer names or prices. Ask the author to retake, crop or blur it and save the new file **under a new name**
   (for example `ladder-spreader-2.jpg`); don't use it as it is.

   **A file that fails check 2 or 3 is still recorded**, so it doesn't come back as untracked every session:
   `folder.py add-asset` with its role, its provenance if known, and notes starting `"rejected: <reason>; not
   uploaded"` (for example `"rejected: a face in the background; not uploaded"`), plus a `folder.py log` line. It is
   never uploaded or used, and its need stays open. The replacement file gets its own entry when it passes.
4. **Provenance.** Ask who took or made it, where and when, unless the author already said. Upload provenance is
   `photo` for a real photo or official image, `screenshot` for a capture of the real system; ask when unsure. Never
   record a drawn or generated picture as a photo. Third-party material needs its rights (`intake.md` § Research rules).
5. **Record it:** `folder.py add-asset --json '{"slug": …, "file": "ladder-spreader.jpg", "role": "photo", "provenance":
   "photo", "rights": "AFI-owned", "notes": "Taken by Jordan Reyes in the repack room, 3 Nov 2026; no faces"}'`.
   A source document gets `"role": "source"` and `"authoritative": true` when the brief lists it as authoritative.
6. **Only then** mark the need done (`mark-need`, with the file name in the note) and log it.

Phone formats are fine: HEIC/HEIF photos and MOV videos are converted on upload. Files are uploaded in the write phase
(`write.md` § 3), not now.

### A pasted image

You can't save an image pasted into the chat, and you can't upload it: `academy_upload_media` needs a file path. Say
so in one line, then give the exact place to save it: the full `assets/` path and a file name ("Please save it as
`ladder-spreader.jpg` in `/Users/jordan/AFI Academy/ladder-safety-repack/assets/`"). You may say what you notice in the pasted
image, but the checks in § 3 run on the saved file. Never say you saved or uploaded it.

## 4. Wait, or a placeholder: the only two ways past a missing item

When an item can't be supplied yet, offer exactly two options, in these words (once for the whole list, not per
item):

- **"Use a placeholder for now. Reviewers will see it on the review page, and it must be replaced before the course
  can be published."** (Safety-critical course. Otherwise: "Use a placeholder for now. Reviewers will see it on the
  review page until it's replaced.") The course is written with a
  `placeholder` image with the shot description, or a visible "TO CONFIRM" note for a fact. In the files this is a
  waiver.
- **"Wait until you have it. I'll keep everything; when you're ready, say 'continue the <title> course'."** The
  course waits until the item exists. Nothing is lost.

**A waiver is only the author's explicit words naming the item or the group**: "use a placeholder for the
ladder-rack photo", "placeholders for all the photos", or a plain "yes" to your one proposal that names the item
(below). These are **not** waivers: "fill it in with anything for now", "whatever you think", "go ahead", "sure",
"would that work?". When the author says one, restate the two options and ask which.

- **"What do you suggest?"** Propose one concrete answer for that item, with a one-line reason, as a yes/no question:
  "I suggest a placeholder for the ladder-rack photo for now, so the draft can go to review. Shall I do that?"
  A yes is the author's choice: record it as theirs. Anything else: restate the two options once.
- **A group waiver** covers only the group the author named. Restate it in plain names before applying it ("Noted:
  placeholders for the 4 photos: the ladder rack, the spreader, the feet and the top step. The facts stay
  open."). Facts and expert items never fall under "all the photos".
- Record each waiver with `mark-need` `"status": "waived"` and the author's words in the note, and log it.
- **Never** fill a missing photo with a drawn image, a stock picture, a generated picture, an icon or a photo of
  something else, and never offer one. The only stand-in is a placeholder the author waived.

**On pause:**
1. If the author gives a date or a promise ("on Thursday", "Dana will send it"), restate it in your own words in
   chat first ("Noted: you'll bring the ladder-rack photo on Thursday 5 November.").
2. Record it: `mark-need` the items answered so far, `folder.py log` a line naming every open item, who supplies it and
   when, and `set-state` with `"phase": "gather"`.
3. Tell the author how to resume: "When you have it, save it in `<full assets path>` and say 'continue the <title>
   course'. I'll keep everything and pick up here." Then stop. Don't write any of the course.

## 5. Done

When `open-needs` returns `[]` (every item done or waived): log it, `set-state` with `"phase": "write"`, and load
`write.md`. **On an update** (`state.json` has `update_of` or `change`): go back to `update.md` instead: § 5 step 6 in the same
session, § 1 step 6 in a later one.
