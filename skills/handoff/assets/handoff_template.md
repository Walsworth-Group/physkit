# Handoff — {{PROJECT}} — {{UTC_DATE}}

> The live handoff. A fresh agent with only this file and the repo must understand the work, trust its
> state, and take the next step. Prior handoffs live in `archive/`; never overwrite them.

## 1. Vision & goal
- **End goal:** <what the work must achieve, concretely>
- **The decision it drives / why it matters:** <one paragraph>
- Full goal: `campaign.md` §Mission · task queue: `results/queue.json`

## 2. Current state (incl. in-flight reasoning)
- **Current best / result:** <value + where it lives (config/snapshot)> · **verification:** <CONFIRMED / PROVISIONAL / unverified> · **metric epoch:** <metric_version · standing; any pending epoch awaiting ratification>
- **Done:** <the settled pieces>
- **In-flight, and why:** <the hypothesis being tested, why, what was expected, what had just been learned>
- **Open threads:** <live questions>
- **Landmines / dead ends:** <known-broken things; directions already ruled out and why (→ `campaign.md` §Known landmines / §Decision record)>

## 3. Run this to confirm state
```bash
# environment
<activate env, e.g. source .venv/bin/activate>
# correctness gates (expect: all pass / suite GREEN)
python scripts/metric.py --selftest
python scripts/run_campaign.py --preflight   # names the metric epoch + its standing
<run the correctness-suite, e.g. make check>
# reproduce the current best (expect: <STATED VALUE> ± tol)
<command that re-derives the current-best number from its snapshot>
```
**Expected output:** <what a healthy state prints, so a mismatch is obvious>

## 4. Roadmap / NEXT (prioritized, goal-linked)
1. <next step> · *serves the goal by …* · <enough detail to act on>
2. <…>
3. <…>
Kept in sync with the JOURNAL NEXT pointer and `results/queue.json`.

---
<!-- On the next handoff: copy this to archive/handoff_<this date>.md, then write a fresh dated file. -->
