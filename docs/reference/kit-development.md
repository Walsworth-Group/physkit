---
id: kit-development
kind: reference-doc
layer: shared
load: on-demand
load_trigger: Before editing the kit itself (a skill, template, reference doc, or CORE) — with
  `improve-kit`, or when adapting an outside method, package, or scaffold into kit content.
frozen: false
review: living
---

# Developing the kit — how kit text is written, sourced, and checked

`improve-kit` is the procedure for changing the kit: triage, sign-off, the frozen core, the change log.
This guide is the craft behind it: how kit content is written, where it lives, how outside material comes
in, and how a change is checked. `campaign-review` names the kit locus a finding should change; this is
how that change is then made well.

## What you are editing

- **The kit source, not a campaign.** A rule that ships lives in `templates/…`, `docs/…`, or
  `skills/<name>/SKILL.md`. A scaffolded campaign is a frozen record of the kit version stamped in its
  `campaign.md`; never patch it to match a newer kit, and never re-sync it against the current CORE. It
  reaches a newer kit only through a deliberate upgrade (`skills/new-campaign/scripts/upgrade_campaign.py`).
- **One statement per rule.** Each rule lives in one place and everything else points to it: `docs/CORE.md`
  for the principles, the skill or reference doc that applies a rule for its depth. A second copy drifts
  from the first and becomes a fork.
- **The map is CORE's routing table.** Adding a skill or reference doc adds its row there; removing one
  removes the row. Skills are found by their `description`, so keep it to one line that says when to use
  the skill.

## How kit text is written

- **Rules are behaviors.** State each rule as something an agent does, not an aspiration ("bound the
  answer before you run it", not "be rigorous"), and tie it to the failure it prevents. A rule no failure
  motivates, or that no observation could show was broken, does not belong (after Zimmer et al., *The
  Agentic Researcher*, arXiv:2603.15914).
- **Why first.** Give the reason with the rule; an agent that knows the failure applies the rule to cases
  its wording did not foresee.
- **Altitude.** `docs/CORE.md` is loaded every turn, so it carries only what binds every turn; depth goes in
  the skill or reference doc an agent reads when the situation arises. Read the neighbors first and match
  their density and voice.
- **Thread every change.** A concept usually appears in several places: a `SKILL.md` body and its
  checklist, a template, CORE or a reference doc, cross-references. Grep for the old wording and update
  every hit; a stale reference is a fork.
- **Readable by someone outside the work.** Kit text does not cite things a user cannot open: your own
  campaigns, internal tracker ids, private files. State the rule and the failure it prevents; the anecdote
  that taught it belongs in your change log, not the kit.
- **Loader-clean frontmatter.** A `SKILL.md` carries only `name` and `description`, so the plugin loader
  accepts it. A reference doc's frontmatter says when to read it (`load`, `load_trigger`) and whether it
  is part of the frozen core (`frozen`).

## Outside material: cite and adapt, never reproduce

Ideas, methods, equations, and algorithms are not copyrightable; their expression is (the prose, the code,
the figures). Kit content built from outside material ships only what is yours: the cited idea,
re-expressed.

- **Re-implement from the source's principles, not its code.** Translating a package line by line into
  another language is a derivative of that code. Work from the paper, the published equations, or the
  documented algorithm, say so in the provenance, and use the package only as an independent check of your
  result. Depending on a package under its license is fine; copying its source into the kit is not.
- **Check the license of borrowed scaffolding.** Another project's skills, prompts, or templates carry
  their own license. Take the pattern and rewrite the prose; never copy another plugin's text wholesale.
- **Quote little, and attribute it.** A brief quote where the exact wording matters, or none. Figures and
  long passages are cited, not reproduced.
- **Every citation is real.** Run `cite-check` on any reference the change adds; a source you cannot
  legitimately access is not a source the kit builds on.

This is a working discipline, not legal advice; where publication or money is involved, a human confirms
it before the material ships.

## Checking a change

- **Templates changed:** scaffold a throwaway campaign and run
  `python skills/new-campaign/scripts/validate_campaign.py <test campaign>`.
- **Doctrine changed:** evaluate on held-out tasks, not only the incident that motivated the change
  (`improve-kit`'s frozen-core rule), and have a fresh agent that did not write it check that nothing in
  the frozen core weakened.
- **Prompts or roles changed:** confirm each rule a role relies on is actually in its rendered context
  (`docs/reference/prompt-surface-audit.md`). The audit scripts check this on a campaign:
  `scripts/audits/audit_prompt_surface.py` (rules present per role), `scripts/audits/audit_input_liveness.py`
  (every quantity a prompt relies on has live data), and `scripts/audits/check_prompt_leaks.py` (no withheld
  value reaches a blind campaign's prompts).
