# Self-check

Two checks on your own draft, before the author sees it: the rubric (before the first save, `write.md` step 6) and the
preview (after the save, step 8). The state phase stays as it is.

## 1. Rubric: score, then fix the two weakest lines

Score the course on each line, 0, 1 or 2, with one line of evidence each (a section id, a quote). Lines marked * are
the ones a safety course can't ship without.

| # | Line | 2 looks like |
|---|---|---|
| 1* | Performance focus | Outcomes are things someone can see the learner do, taken from "what goes wrong", not topics |
| 2* | Practice matches the outcome | Practised with the same verb (decide → a decision on a photo) |
| 3 | Practice density | Floor: practice at least every 3 sections; 30% or more of sections ask the learner to do something |
| 4* | Grounding | Scenario, story and wrong options come from the real case or the expert's words |
| 5 | Feedback teaches | Every option's feedback gives the why and the consequence in 1–2 lines |
| 6* | Real visuals | Every step and hazard shows the real thing (photo, screenshot or official image); drawn only for concepts |
| 7 | Rhythm | The kit's rhythm rules pass; a moment in every lesson; no wall of text |
| 8 | One idea per section | The title states the idea; the body supports only that |
| 9 | Voice | Plain, concrete, imperative, no filler; the Spanish reads as written by a Miami supervisor, in *usted* |
| 10 | Length honesty | The time estimate is within 20%; nothing could be cut without loss |
| 11* | Safety integrity | No hazard text hidden in a reveal; danger only for real, cited hazards; every number cited |
| 12 | Take-away | The recap and the job aid work on the floor without the course |

**The bar:** 16 of 24 or more, with every * line at 1 or more, before the draft goes to review. A safety course
(`safety_skill`) needs every * line at 2 by the time it's published; reviewers confirm that, not you.

1. Write the scores to the log (`folder.py log`: "rubric: 1:2 2:2 3:1 …, total 21/24").
2. **Pick the two lowest lines** (on a tie, a * line first). Fix both in `course.json`. A line you can't fix without
   something from the author (a real quote, a photo) stays as it is: say what would fix it.
3. **Spanish register: usted, never tú.** Scan every Spanish string in `course.json` for tú forms: imperatives
   such as "sigue", "revisa", "usa", "lee", "pregunta", "abre", "llama", and "tu", "tus", "te", "contigo". Rewrite
   each in usted: "siga", "revise", "use", "lea", "pregunte", "abra", "llame", and "su", "sus", "le", "con usted". A
   sentence that mixes the two ("Sigue … con su supervisor") is a tú form too. Answer options, quiz questions and
   feedback count too: "Escanee el código", not "Escanea el código".
4. Validate until there are no errors, then save (`write.md` § 6). Don't score again.
5. Those two lines, after the fix, are **the two weakest points** for the hand-over, in one plain sentence each,
   about the learner and what would fix it ("Only a few screens ask people to do something; I added two questions.
   A real story from the floor would help most."). Never the rubric's line names, scores or percentages. Also flag in
   the hand-over, the same way, every * line still below the bar (below 1; for a safety course, below 2).

Your score is a self-check, not the review: never present it as approval.

## 2. Look at the preview

After the save, the draft has a `preview_url`. Look at it the way learners will see it, if you can:

- **A browser tool is available** (for example Claude Desktop's built-in browser): open the `preview_url`, set the
  width to 375 px, switch the player to Spanish, and go through every section; then do the same at a desktop width
  (an English pass is optional).
  Look for clipped text, walls of text, missing or wrong images, English left in the Spanish, and buttons that don't
  fit. Fix what you find in `course.json` (pull first: `write.md` § 1), validate, and save a new revision with a note.
  If the page asks for a sign-in, ask the author to sign in in that browser themselves, then carry on. **Never type,
  ask for or store a password, code or key.**
- **No browser tool, or the author can't sign in:** rely on `academy_validate` and the rubric, and say so in the
  hand-over, in one line: "I couldn't look at the preview myself (the Academy's checks found no errors). Please open the link
  on your phone, switch to Spanish, and check that no text is cut off."

Record the method in the log, every time: `folder.py log` "preview check: browser, 375 px ES, then desktop" or
"preview check: not possible (no browser); validator and rubric only".
