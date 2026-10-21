# Brief fields, origins and approval

The brief is `brief.json` in the course folder (`folder.py root` + `/<slug>/`). Its shape is the `Brief` model in the
kit's `brief_schema` (`academy_kit`): unknown keys are errors. Most fields are `{"value": …, "origin": …}`.

## Origins

Every field records where its value came from. Get it right: the brief shows it to the author and reviewers.

| Origin | Use when |
|---|---|
| `said` | The author said it or picked it, including a recommended option they chose. A value they changed is `said`. |
| `inferred` | You worked it out: from their words, the sources, the research, or the original course (spin-off). |
| `default` | It came from the course type's or the audience's default, including every "decide for me". |

- A value the author states stays `said` **even when it equals the default** (the author says "80 percent": `said`).
- A field you first inferred or defaulted and the author later answers or confirms becomes `said`.
- Always-asked fields are `said` once they have a value (§ Fields). The one exception is `expertSeenBrief`: it is
  `not_yet` / `inferred` on each new version until the author answers, and stays so when there is no expert
  (§ Approval, steps 1, 6 and 7).

## Course type

Pick by what the learner must **do** after the course (mark it `inferred` and show it):

- `policy_ack`: know a policy and acknowledge it (PTO requests, a code of conduct). → `course-types/policy_ack.md`
- `safety_skill`: perform a physical procedure correctly where a mistake can hurt someone (a pallet-jack check
  before use, using a fire extinguisher, lockout). → `course-types/safety_skill.md`
- `awareness`: notice, recognise and report (heat illness signs, an annual refresher). → `course-types/awareness.md`

In chat, name the type in plain words, never by its id: "a policy to read and confirm", "a safety skill to do
correctly", "a course to notice and report".

Safety-critical is a separate, always-asked answer: an `awareness` course can be safety-critical.

## Fields

**Asked** = always asked outright, never inferred, never defaulted, never "decide for me". A value goes on the brief only
when the author gave it or said yes to your one proposal (`intake.md` § Question rounds); it is then `said`. Until then
the field stays empty and sits in `stillNeeded` as "Needs your answer: <plain question>". Ask with the wording in the last column (adapt it to the topic, keep it plain). "Type file" = the default in
`course-types/<type>.md`.

| Group | Key | Applies | Asked | Default | Plain question |
|---|---|---|---|---|---|
| Purpose | `title` (`{en, es}`) | always | | inferred | "What should the course be called?" |
| | `author` (plain string) | always | | `academy_kit`'s `you` when present | "What name should go on the brief as the author?" (only if `you` isn't given) |
| | `goal` | always | | inferred | "In one sentence, what should people do differently after this course?" |
| | `whyNow` | always | | inferred | "Why is this course needed now: a new rule, an incident, an audit, new hires, the yearly refresher?" |
| | `wrongToday` | always | | inferred | "What do people get wrong today? The top one to three things." |
| | `realCase` | `safety_skill`, `awareness`; optional for `policy_ack` | **Asked** (`safety_skill`, `awareness`) | – | "Tell me about one real time this went wrong (or nearly did) here. Leave the names out." |
| | `outcomes[]` (`id`, `text`, `practisedIn`, `testedBy`) + `outcomesOrigin` | always (2–5) | | inferred | "After the course, what should people be able to do that someone could see?" |
| | `supervisorCheck` | always | | inferred | "How will a supervisor know someone can do it: watching them, a practical check, or not at all?" |
| Classification | `topic` | always | | inferred | "What's the topic, in a few words?" |
| | `area` | always | | inferred | "Which area and department is this for?" |
| | `courseType` | always | | inferred (§ Course type) | "Is this mainly a policy to acknowledge, a safety skill to do correctly, or something to notice and report?" |
| | `safetyCritical` | always | **Asked** | – | "Could someone get hurt if they get this wrong?" |
| Audience | `who` | always | | inferred | "Who takes it: which roles, which sites?" |
| | `languageFirst` | always | | floor: Spanish first; office: English first | "Which language should come first?" |
| | `readingLevel` | always | | floor: grade 6; office: grade 9 | "How simple should the reading be?" |
| | `device` | always | | floor: shared tablet or phone; office: computer | "Where will they take it: phone, shared tablet, computer?" |
| | `priorKnowledge` | always | | inferred | "What do they already know about this?" |
| | `otherLanguages` | when needed | | – | "Does anyone need a language other than English or Spanish?" (v1 can't: add a line to `limits`) |
| Sources | `sources[]` | always | **Asked** (the authoritative ones) | – | "Which documents are the final word on this: the regulation, an AFI policy or program, a manual?" |
| | `expert` | always | **Asked** | – | "Who is the expert who will check the facts and steps before anyone takes the course?" |
| | `expertSeenBrief` (`yes` / `not_yet`) | safety-critical | **Asked**, with the brief (§ Approval) | `not_yet` on a new version | "Has <expert> seen this brief yet?" |
| | `sources[].rights` | third-party material | yes, when there is any | – | "Does AFI have the right to reuse this material, or should I only learn from it?" |
| | `stillNeeded[]` (`text`, `who`) | always | | inferred | AFI-specific gaps and open conflicts; "Who can tell us …?" `who` is the person the author named, or "to be named"; the author only for their own answers or a task they took on |
| Format | `contentKinds[]` + `contentOrigin` | always | | type file (asked in the media round, `intake.md` § 3) | The media question round: voice, video, drawn illustrations; real photos or screens |
| | `length` | always | | type file | "How long should it be?" |
| | `lessons[]` + `lessonsOrigin` | always | | inferred (one line each, not a storyboard) | – (shown for correction) |
| | `jobAid` | `safety_skill`, `awareness` | | type file | "Would a one-page card for the floor help?" |
| Assessment | `finalTest` | always (null when no test) | | type file | "Should there be a test at the end?" |
| | `practice` | always | | the kit's rhythm rule (type file) | – |
| | `difficulty` | if test | | applied questions | – |
| | `passMark` (integer) | if test | **Asked** | – | "What score should people need to pass?" |
| | `mustPass` | if test | **Asked** | – | "Which questions must everyone get right, because a wrong answer could hurt someone?" |
| | `handsOn` | always; **Asked** if safety-critical | **Asked** (safety-critical) | type file (when asked: offered as the recommended answer) | "Does someone need to watch each person do it before they're signed off?" |
| | `acknowledgement` | `policy_ack` | | type file | "Should people confirm they've read and understood it?" |
| After launch | `certificate` | always | | type file (asked in the media round, as the recommended option) | "Should people get a certificate, and for how long is it valid?" |
| | `reviewers` | always | | inferred (expert; Spanish reviewer required if safety-critical) | "Who should review the draft?" |
| | `publisher` | always | | – | "Who will press Publish after the review? It has to be someone other than you." |
| | `pilotRun` | safety-critical | | type file (3–5 real learners) | "Can 3 to 5 people from the floor try it before it goes out?" |
| | `readyBy` | always | | – | "When does it need to be ready?" |
| | `reviewAgain` | always | | type file | "When should we look at it again?" |
| | `updateOwner` | always | | inferred | "Who tells you when something changes, like a new chemical or a new rule?" |
| Limits | `limits[]` (plain strings) | always; **Asked** if safety-critical | **Asked** (safety-critical) | inferred | "What can't this course do on its own? For example, replace hands-on training." |
| Update only | `change`, `changeNote` | never on a new or spin-off brief | | – | – |

Authoritative sources: each entry has `id` (S1, S2 …), `title`, `role` (`authoritative` / `background`), `use`, `rights`,
and for authoritative ones a `url` (when one exists, `https://`), an `asOf` date and a quoted `excerpt` (see
`intake.md` § Research rules). When the source is the author's own document, read it and quote the words yourself,
with its revision and date; ask the author only for what you can't read in it (for example, it has no date).

## Approval

0. **Show the brief** when every applicable field is filled and every always-asked question has been asked (and, after
   "you decide", proposed once). An always-asked field the author hasn't answered stays empty, listed in `stillNeeded`
   as "Needs your answer: <plain question>" (`who`: the author); never put a value there to make the brief complete.
   "Has the expert seen this brief?" is asked with the brief (step 5).
1. **Write `brief.json`.** `version` 1 the first time; add 1 every time its content changes after the author has seen
   it. Recording `artifactUrl`, `approvedVersion` or `approvedAt` never changes `version`. `approvedVersion` and
   `approvedAt` stay empty until approval. (One exception: recording an update's `change` and `changeNote` doesn't
   change `version`, `update.md` § 5 step 4.) For a safety-critical course, a new version starts with `expertSeenBrief`
   `{"value": "not_yet", "origin": "inferred"}` (no one has seen this version yet). Record `folder.py set-state --json
   '{"slug": …, "phase": "brief", "brief_version": N}'`.
2. **Validate:** `academy_validate_brief` with the file path. Fix every error you can; if a fix needs an answer, ask the
   author. Errors on always-asked fields the author hasn't answered are expected: say so, and never invent a value to
   make it validate. Validation must pass (no errors) only before approval is recorded (step 7).
3. **Render:** `render_brief.py <slug>` writes `brief.html` (it doesn't need a passing validation). Never hand-write the
   HTML. If it fails because an open field is one the page needs (for example safety-critical), show the brief in chat
   instead: every field with its origin, the open ones marked "Needs your answer".
4. **Publish** `brief.html` with the Artifact tool (icon `document` the first time). After the first publish, store the
   link in `brief.json` as `artifactUrl`, render and republish once, so the page shows its own link. For each new
   version, republish the **same file path**, so the link stays the same. In a later session, republish with `url` =
   the stored `artifactUrl`; if the tool refuses, read the page as it says, then publish. If you still get a new link,
   store it as `artifactUrl` and tell the author the link changed. If the Artifact tool isn't available or the
   publish is refused, say it plainly and give the local path: "I couldn't put the brief online, so here is the file
   on your computer. Open it in your browser: <path>". Open it with a browser tool if you have one.
5. **Message the author:** the link (or path), then a 3-line summary:
   - what it is: the kind of course in plain words, who takes it, language first, length and lessons;
   - how it's checked: the test and pass mark, the must-pass questions, the hands-on sign-off, the expert;
   - what you chose for them: the answers tagged *Claude's guess* and *Standard choice*, by name, in plain words, and what's still
     needed and from whom.

   Explain the tags once, in one plain sentence: "Each answer on the page is tagged *You said*, *Claude's guess*
   (please check these) or *Standard choice* (the usual for this kind of course)." If the author can't open the page
   (no link and no browser), list every field in chat with its tag instead. If any always-asked field is open, say
   plainly: "The brief can't be approved until you answer: <plain question>." For a safety-critical course with a named
   expert, ask here: "Has <expert> seen this brief yet?" (when the expert is "None (author's decision)", don't ask; it
   stays "not yet"). Then end with: "Nothing is built until you approve this brief. Reply
   **approved**, or tell me what to change."
6. **The expert-seen answer.** "Not yet" matches the page: set its origin to `said`, render and republish; the version
   stays. "Yes" is a change: new version (step 1, with `{"value": "yes", "origin": "said"}`), validate, render,
   republish, and ask for approval of the new version.
7. **Only an explicit approval in chat** of the brief you showed counts: "approved", "looks good, approved", "yes,
   build it". **Refuse approval while any always-asked field is empty**: say which, and ask it ("approved" never
   answers it). When the author answers: record it as `said`, remove it from `stillNeeded`, add 1 to `version`,
   validate, render, republish and ask for approval again. For a safety-critical course whose expert-seen question is
   still unanswered, ask it first (step 6), unless the expert is "None (author's decision)": then don't ask it, and
   `expertSeenBrief` stays `{"value": "not_yet", "origin": "inferred"}`. Validation must show no errors. Then set `approvedVersion` = `version` and `approvedAt` = now (ISO 8601, UTC), validate, render and
   republish, then `folder.py set-state` with `"phase": "gather", "approved_version": N`, log it, and load
   `gather.md`.
8. **Anything else is not approval.** A change: apply it, add 1 to `version`, validate, render, republish, ask again.
   "You decide", "whatever", "sure" without the brief in front of them: show the brief and ask for an explicit yes.
