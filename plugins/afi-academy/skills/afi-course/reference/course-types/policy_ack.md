# Course type: `policy_ack`

**Pick it when** the learner must know an AFI policy and confirm they've read it: PTO requests, a code of conduct, a
handbook change.

## Defaults

| Length | Lessons | Test | Pass mark | Certificate |
|---|---|---|---|---|
| about 10 min | 1–2 | 1–2 checks, no pool (no final test) | n/a | none; acknowledgement only |

Other defaults (mark them `default`):
- `finalTest`, `passMark`, `mustPass`, `difficulty`: empty (no test). If the author wants a test, it becomes `said`, and
  the pass mark and must-pass questions are then **asked**.
- `practice`: 1–2 checks on what the policy means for the learner.
- `acknowledgement`: the learner confirms they read and understood the policy.
- `handsOn`: none.
- `contentKinds`: mostly text; real screenshots if the policy involves a system (for example where to request PTO).
- `reviewAgain`: when the policy changes, or 12 months.

## Structure

The kit's writing guide, **Recipes → Policy acknowledgement (`policy_ack`)**.

## Fields that apply

All of `brief-fields.md`, plus `acknowledgement`. Not `jobAid` or `pilotRun` (unless safety-critical). `realCase` is
optional: ask for one only if it would make the policy concrete.

## Research starting points

- **The AFI policy itself is the authoritative source** (handbook section, policy document, with its revision date and
  the excerpt relied on). Ask the author to drop it into `assets/`; don't write the policy from memory or from other
  companies' policies.
- The policy owner is usually the expert of record (still **asked**).
- Outside research only where the author asks or the policy points to a law (for example a state leave law), cited to
  the section.
