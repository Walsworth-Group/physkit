# Kit Review — <CAMPAIGN NAME>

> Retrospective on a finished/paused autoresearch loop, to harvest **kit** improvements. **Every finding
> cites its evidence; every number is recomputed from the ledger, never estimated.** Keepers feed
> `improve-kit`.

| | |
|---|---|
| **Campaign** | <name> |
| **Directory** | <path> |
| **Transcripts** | <path(s) to the `*.jsonl`> |
| **Kit version at run** | <the stamp in `campaign.md` / `results/logbook.md`> |
| **Dates** | <start> → <end> |
| **Agent model(s)** | <loop model; sub-agent models> |
| **Reviewer** | <name> |

---

## 1 · Timeline & decision chain
*Experiments, decisions and their reversals, disputes, user interventions, compute spent — in
order. For each decision, the hindsight provenance/confidence it was acted on at.*

| # | event / decision | provenance at the time | outcome (held / reversed) | source |
|---|---|---|---|---|
| | | PINNED / REPORTED / INFERRED / RECALLED / REASONED | | (cite artifact/transcript) |

---

## 2 · What worked — keep it
*The places the scaffolding caught an error, forced a useful check, or enabled clean recovery. Don't drop
these in a fix-list — they are the parts to protect.*

- …

---

## 3 · Findings → proposed kit changes
*One row per finding. Evidence is a citation (a transcript record id / artifact + line), not a paraphrase.
Root cause names the mechanism. Target file is the exact kit locus to change. Bucket: auto / sign-off /
more-context (anything touching the integrity-verification core → sign-off).*

| # | observation | evidence | root cause | proposed kit change | target file | bucket |
|---|---|---|---|---|---|---|
| 1 | | | | | | |

---

## 4 · Keepers for `improve-kit` (bucketed)
*The subset of §3 to actually apply. This is the hand-off list: `improve-kit` marks each row `applied`
(with the commit or date) or `rejected` (with the reason). The review is closed only when no row is
`pending`.*

| # | keeper (from §3 row) | bucket | target file | status | applied in / reason |
|---|---|---|---|---|---|
| K1 | | auto / sign-off / more-context | | pending | |

> Honesty-core guard: none of the above weakens integrity, verification, or the frozen metric. ✔ / explain.
