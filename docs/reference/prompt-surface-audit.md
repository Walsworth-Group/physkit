---
id: prompt-surface-audit
kind: reference-doc
layer: shared
load: on-demand
load_trigger: Before launching any loop or subagent architecture that relies on doctrine; when an agent
  violates a rule it "should" know; when auditing how contamination could enter a rendered context.
frozen: false
addresses: [9, 1]
status: new
review: 2026-08-06
---

# Prompt-surface audit — doctrine only governs an agent whose rendered context contains it

A rule that is "in the kit" is not thereby in force. Doctrine reaches an agent through a specific,
enumerable set of surfaces, and each surface has its own failure mode. The discipline: **before relying
on a rule, verify it is physically present in the RENDERED context of every agent expected to obey it —
and re-verify after every prompt change.** This is the prompt-side twin of *enforce, don't exhort*
(`PRINCIPLES.md` Ctx 9): that rule says wire the check as a gate and assert the gate is present; this one
says the same about the doctrine itself.

## The surfaces (and how each one fails)

| Surface | Reaches | Failure mode |
|---|---|---|
| Project `CLAUDE.md` | the main session only | re-injected every turn, but **only** for sessions started in the folder after it existed |
| An opened doc | the main session | falls out of context over a long session (why `CORE.md` is imported, not read) |
| Subagent / Task prompts | that subagent only | the prompt **replaces** the doctrine stack — subagents inherit *nothing* from CLAUDE.md unless the prompt author put it there |
| SDK-spawned loop roles (generation / critic / ranking prompts) | that role only | a custom loop may load **no** always-on files at all — the Agent SDK loads none by default unless `setting_sources` includes `'project'`; every rule the role needs must be authored into its prompt template |
| Dynamically rendered evidence (observation digests, literature excerpts, scoreboard summaries) | every role that receives them, every round | not authored but *generated* — can silently omit relied-upon framing, or carry **stowaway contamination** (stale narratives, false facts) that no static file contains |
| **Harness-injected instruction** (model-conditional system-prompt bundle) | every agent on that model | authored by neither you nor the kit, present in **no** file you can grep, gated on the **model ID** — and it can *contradict* doctrine, not merely omit it |

The **dynamically rendered** row is the one audits miss: checking the static prompt files is not checking
the prompt surface. Anything rendered at runtime is part of the surface and must be audited **as rendered**.

The **harness** row fails in the opposite direction from every other. The rest fail by **omission** — the
rule isn't in the render. This one fails by **contradiction**: the doctrine is present, intact, and
outranked by an instruction the kit never wrote. Grep for your rule and the audit passes. So audit both
directions — is the rule there, and is anything there that opposes it?

## The audit

1. **Enumerate the agent roles.** Main session, every subagent type, every SDK loop role, every scheduled
   job. An architecture diagram with one box per distinct context.
2. **List the relied-upon rules per role.** Which disciplines does the design *assume* each role obeys
   (safety caps, honesty rules, method disciplines, required-key contracts)? If the campaign has a
   charter, its rules are the checklist.
3. **Obtain each role's context AS RENDERED** — not the template: run the renderer and capture what the
   agent actually receives, including the dynamically generated blocks.
4. **Grep the render for each rule.** A rule not literally present (or not entailed by text that is) is
   not in force for that role — either add it to that surface or stop relying on it there. **Then grep for
   its opposite** — a rule that is present but countermanded is not in force either.
5. **Audit the dynamic blocks both ways:** missing doctrine in, and contamination out — does the render
   carry any claim, framing, or value that the campaign's isolation/honesty design forbids?
6. **Re-run on every prompt change, and gate the launch on it.** The audit is cheap and mechanical; wire
   it into the pre-launch checklist (`new-campaign` Step 5) rather than trusting that it happened.

## Three dated episodes (why this earns a doc)

- A hardware campaign's loop violated two disciplines its designers relied on — a calibration-key
  contract on emitted experiments and a simulate-before-attributing honesty rule — and the post-mortem
  found both were simply **absent from the loop's rendered prompts**: the SDK-spawned roles inherited no
  CLAUDE.md or global doctrine, and nobody had checked the rendered surface against the assumed rule
  list. Both holes bit mid-run, each costing real instrument time (2026-07).
- The same program's leak audit checked every static prompt source and stayed green for two entire
  campaign arms — while a **dynamically rendered** observation digest carried a stale, false fact about
  the physical sample into every generation and critique context of both arms. The static files were
  clean; the surface was not (2026-07).
- A CLI release began appending *"Do not call the AgentTool unless the user requested it"* to every session
  on one model — compiled into the binary, gated on a model capability flag, so it sat in no settings file
  and on no other model. Agents then skipped the prescribed independent refuter and substituted controls of
  their own design; in one session two headline correlations (r = 0.873, 0.879) reached a report before a
  belated independent check scored the *wrong-configuration* control at 0.882 — the correspondence carried
  no configuration information. Every kit file was correct; a rule the kit never wrote outranked them
  (2026-08).

## Composition

`PRINCIPLES.md` Ctx 9 (*enforce, don't exhort* / *assert the gate is present*) is the parent doctrine ·
`new-campaign` Step 5 wires the audit into the launch checklist · `campaign-status` hygiene checks are
the natural place to re-assert it mid-campaign · `context-economy.md` governs *how much* context each
role gets; this doc governs *whether the load-bearing rules are in it*.
