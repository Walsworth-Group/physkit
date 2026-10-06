---
id: prompt-surface-audit
kind: reference-doc
layer: shared
load: on-demand
load_trigger: Before launching any loop or subagent architecture that relies on doctrine; when an agent
  violates a rule assumed to be in force; when auditing how contamination could enter a rendered context.
frozen: false
addresses: [9, 1]
status: new
review: living
---

# Prompt-surface audit — doctrine only governs an agent whose rendered context contains it

A rule present in the kit is not thereby in force. Doctrine reaches an agent through a specific,
enumerable set of surfaces, and each surface has its own failure mode. Before relying on a rule,
verify it is physically present in the rendered context of every agent expected to obey it, and
re-verify after every prompt change. This is the prompt-side counterpart of *enforce, don't exhort*
(CORE, Running unattended): that rule requires wiring the check as a gate and asserting the gate is
present; this one requires the same of the doctrine itself.

## The surfaces (and how each one fails)

| Surface | Reaches | Failure mode |
|---|---|---|
| Project `CLAUDE.md` | the main session only | re-injected every turn, but only for sessions started in the folder after it existed |
| An opened doc | the main session | falls out of context over a long session (why `CORE.md` is imported, not read) |
| Subagent / Task prompts | that subagent only | the prompt replaces the doctrine stack; subagents inherit nothing from CLAUDE.md unless the prompt author put it there |
| SDK-spawned loop roles (generation / critic / ranking prompts) | that role only | a custom loop may load no always-on files at all: the Agent SDK loads none by default unless `setting_sources` includes `'project'`; every rule the role needs must be authored into its prompt template |
| Dynamically rendered evidence (observation digests, literature excerpts, scoreboard summaries) | every role that receives them, every round | not authored but generated, so it can silently omit relied-upon framing, or carry **stowaway contamination** (stale narratives, false facts) that no static file contains |
| Harness-injected instruction (model-conditional system-prompt bundle) | every agent on that model | authored by neither the user nor the kit, present in no file that can be grepped, gated on the model ID, and able to contradict doctrine rather than merely omit it |

The dynamically rendered row is the one audits miss. Checking the static prompt files is not checking
the prompt surface. Anything rendered at runtime is part of the surface and must be audited as rendered.

The harness row fails in the opposite direction from every other. The rest fail by omission: the rule
is not in the render. This one fails by contradiction. The doctrine is present, intact, and outranked
by an instruction the kit never wrote, so a grep for the rule passes while the rule is not in force.
Audit both directions: is the rule present, and is anything present that opposes it?

## The audit

1. **Enumerate the agent roles.** Main session, every subagent type, every SDK loop role, every scheduled
   job. An architecture diagram with one box per distinct context.
2. **List the relied-upon rules per role.** The disciplines the design assumes each role obeys: safety
   caps, honesty rules, method disciplines, required-key contracts. If the campaign has a charter, its
   rules are the checklist.
3. **Obtain each role's context as rendered.** The template is not the render. Run the renderer and
   capture what the agent actually receives, including the dynamically generated blocks.
4. **Grep the render for each rule.** A rule not literally present, and not entailed by text that is, is
   not in force for that role. Add it to that surface or stop relying on it there. Then grep for its
   opposite: a rule that is present but countermanded is not in force either.
5. **Audit the dynamic blocks both ways:** missing doctrine going in, and contamination coming out. Check
   whether the render carries any claim, framing, or value that the campaign's isolation and honesty
   design forbids.
6. **Re-run on every prompt change, and gate the launch on it.** The audit is cheap and mechanical. Wire
   it into the pre-launch checklist (`new-campaign` Step 5) rather than trusting that it happened.

## Three dated episodes (why this earns a doc)

- Spawned roles inherit no always-on doctrine. A discipline the design relies on (a calibration-key
  contract on emitted experiments, a simulate-before-attributing honesty rule) governs such a role only
  if the role's own prompt template carries it. Check each spawned role's render against the assumed rule
  list before launch; an absence found after the run has already cost instrument time.
- A leak audit restricted to static prompt sources can stay green across entire campaign arms while the
  surface is contaminated. Dynamically rendered evidence is regenerated each round and can carry a stale
  or false fact about the physical system into every generation and critique context while no static file
  contains it. Audit the render, not the sources.
- Harness-injected instruction can countermand a prescribed step. An instruction compiled into a CLI and
  gated on a model capability flag sits in no settings file and reaches only the agents on that model; if
  it suppresses a prescribed independent refuter, agents substitute controls of their own design. A
  correlation that has not been scored against a wrong-configuration control is not evidence: the control
  can score as high as the result, in which case the correspondence carries no configuration information.
  Grep the render for the opposite of each relied-upon rule.

## Composition

CORE's *enforce, do not exhort* (Running unattended) is the parent doctrine ·
`new-campaign` Step 5 wires the audit into the launch checklist · `campaign-status` hygiene checks are
the natural place to re-assert it mid-campaign · `context-economy.md` governs how much context each
role gets; this doc governs whether the load-bearing rules are in it.
