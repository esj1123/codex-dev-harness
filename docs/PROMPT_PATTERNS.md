# Prompt Patterns

## Purpose

Provide reusable prompt patterns for Codex work requests as clear task contracts.

These patterns are documentation-only. They do not execute tasks, grant side-effect approval, create runtime code, or bypass project safety policies.

## Choose The Requested Result

Infer the workflow from the request; do not ask users to classify routine work.
Use the short patterns below first. Read the target's applicable instructions
and resolve facts from existing evidence before asking about missing decisions
that would materially change the output.

| Work | Default output and checks |
|---|---|
| Inspection or explanation | Answer the question with relevant evidence and uncertainty; no new file, package, or tests merely to supply an answer. |
| Document authoring or revision | Use the existing format, sources, and user decisions; check content, format, source support, and current open items. |
| Coding or automation | Make the scoped change in existing modules; verify affected behavior and required integration conditions. |

Common guidance is goal, scope, source protection, existing approval, necessary
checks, and a concise result. Reuse decisions for the same target, action, and
scope. Keep current acceptance separate from later finalization; missing
required approval or evidence remains a current blocker. Mixed tasks use the
checks relevant to each changed surface. Do not turn document production into
authoring-system, schema, or converter development without that scope.

Target rules still apply. Durable edits to the Harness itself use
`CHANGE_CONTROL.md` and `VERIFICATION.md`, including required integration checks.
The short patterns do not waive those rules or inherited global instructions.

## Optional Workflow Skills

Select a specialization from the requested output, without making the user name
a workflow. Common inspection/document/coding guidance stays the entrypoint.
Use only the specialization relevant to the changed surface; a mixed document
and drawing task may use both. Select document family, design perspective,
stage and format details only as needed. Review-only work uses the review role;
authorized review-and-correction continues into authoring within the existing
scope. Author self-checks and independent review are distinct. A skill adds
judgment guidance, not another
mandatory task form, approval loop, receipt, or verification tier.

| Work type | Boundary and current implementation |
|---|---|
| Engineering documents | [harness-engineering-documents](workflows/harness-engineering-documents/SKILL.md): author engineering documents, derive/select/allocate designs and update related outputs; preserve project formats, IDs, sources and provisional decisions. Families include requirements, hardware/software design, interfaces, lists/calculations, tests and operations. |
| Engineering diagrams | [harness-engineering-diagrams](workflows/harness-engineering-diagrams/SKILL.md): objects, dimensions, layout, connectivity, frames/symbols and native editability; CAD guidance is conditional. Distinguish design, visual and native checks. |
| Engineering review | [harness-engineering-review](workflows/harness-engineering-review/SKILL.md): inspect original inputs, project criteria and actual candidates using relevant perspectives; scope findings, missing coverage and corrections. Review-only grants no writes; optional sibling references are not prerequisites. |
| Education and knowledge content | Design only: start from the learner outcome and existing teaching format; preserve authority-source/derived-preview direction, learner blanks, assessment/rubric contracts, and module scope. Authoring quality and learner acceptance are separate. Implement only when a target owner selects a bounded need. |
| Legacy system and logic analysis | Design only: answer the bounded behavior or dependency question from identity-bound source evidence; distinguish observed behavior, inferred logic, and missing native/runtime evidence. Preserve originals and unresolved mappings; do not turn analysis into rewrite or live control. Implement only when a target owner selects a bounded need. |

Ordinary meeting notes, weekly reports, simple prose edits, and coding use their
existing short patterns. Skill descriptions carry these trigger boundaries;
automatic discovery remains enabled. Neither deferred type has an empty skill
folder or an automatic trial requirement.

### Installation And Use

The repository directories above are the shared source. With installation
authorization, copy each selected directory's `SKILL.md` and all of its current
`references/*.md` files byte-for-byte into the personal locations selected for this local setup,
preserving relative paths:

- Codex: `~/.codex/skills/<skill-name>/`
- Claude Code: `~/.claude/skills/<skill-name>/`

These locations are local installation choices; on another installation, resolve
its configured discovery roots before copying. Inspect the exact destination first.
Reuse an identical copy. An authorized update may replace a file matching its
previous recorded installation; preserve other different or unrecognized contents
and resolve that installation separately. Check new reference destinations too.
Do not overwrite unrelated skills, add symlinks/hooks, or change
global AGENTS/CLAUDE settings. Later updates require an explicitly scoped copy
and comparison; there is no automatic sync or installer service.

In a fresh session, request the engineering task naturally or name the skill:
`$harness-engineering-documents`, `$harness-engineering-diagrams` or
`$harness-engineering-review` in Codex, with the corresponding `/` name in Claude.
Confirm discovery and actual skill reading through the tool's runtime evidence;
installation hashes alone do not prove loading. A synthetic read-only smoke
demonstrates loading in that invocation, not automatic selection for every future
request, native application behavior, or adoption by existing project sessions.

This setup distributes the three engineering skills together with sibling relative
references. Review remains usable without optional sibling references: use the
core review method and project sources, and state only the actual evidence gap.
Check installation hashes, actual loading and synthetic behavior separately in
the current STATUS closeout; none establishes real document acceptance.

Keep the catalog here and detailed role rules in the three SKILL.md files.
References are conditional guidance with synthetic examples and no project
technical authority. The manifest classifies
the skill rules without expanding the common Read Order or protocol namespaces.

## Reusable Prompt Template Files

Use these files as copy-ready prompt contracts when a task needs more structure
than the short patterns below. Copy only applicable sections, retaining every
field required by the selected contract; do not print empty or NOT APPLICABLE
rows for unselected workflows. A separate receipt file is required only when
the task or applicable policy requires one:

| template | use when |
|---|---|
| `prompts/task_contract/task_contract.md` | a task needs a detailed scope; package and execution sections apply only under their stated conditions |
| `prompts/task_contract/critic_review.md` | requesting review-only correctness, safety, scope, and evidence review |
| `prompts/task_contract/verification_closeout.md` | recording changed files, commands, evidence, safety checks, risks, and next step |
| `prompts/task_contract/release_summary.md` | summarizing release state without creating tags, moving tags, publishing, or generating artifacts |

These prompt templates do not grant approval by themselves.

For closeouts that need audit-style receipt structure, use
`docs/AUDIT_TRACE_SCHEMA.md` as the field reference. The schema defines what to
summarize, but it does not authorize prompt capture, tool-call body capture,
private raw data capture, audit logging automation, or receipt file generation.

Write/apply actions still require human approval when they cross side-effect
boundaries such as deletion, moving files, external sends, dependency or
environment mutation, workflow installation, release publication, manifest,
checksum, SBOM, provenance, eval harness implementation, audit logging
implementation, RAG implementation, application code, device code, or live-write
behavior.

## Basic Task Contract Structure

A well-scoped Codex task should state:

- goal
- target repo or path
- read-only vs write scope
- allowed files
- forbidden files or actions
- necessary content or behavior checks; executable commands only when applicable
- the useful result and remaining decisions
- side-effect approval boundary

## Coding Simplicity Clause

For coding tasks, include this clause when scope risk is non-trivial:

```text
Coding simplicity:
- Prefer the nearest existing module, symbol, helper, test, or documented pattern.
- Do not add a new file, shared utility, package, gate, profile, example,
  workflow, or automation unless it is required for this task and explicitly
  approved.
- Keep documentation-only, test-only, cleanup-only, and runtime behavior changes
  separate when practical.
- Use focused verification that matches the changed surface.
- Do not weaken safety, private-data, approval, or live-write boundaries.
```

This clause is task-contract guidance only. It does not authorize code changes,
side effects, workflow installation, eval quality-gate integration, RAG/index
tooling, audit automation, release artifact generation, profiles, examples, or
downstream writes.

## Pattern: Implementation Task

Use only when implementation is explicitly approved.

```text
Goal:
Implement [specific behavior].

Target:
[repo/path]

Allowed files:
- [specific file or folder]

Forbidden files/actions:
- [specific no-touch files]
- no unrelated refactor
- no live/device/runtime side effects unless explicitly approved

Verification:
- [test command]
- [quality gate command]

Completion report:
1. changed files
2. behavior summary
3. verification result
4. safety checks
5. known risks
```

## Pattern: Review-Only Task

Use for explanations, investigations, comparisons, and reviews without edits.
Answer the requested question first; a formal verdict is needed only when the
request calls for one.

```text
Goal:
Review [scope] and report findings.

Target:
[repo/path]

Write scope:
Read-only. Do not edit files.

Review criteria:
- correctness
- safety
- source-use compliance
- evidence gaps relevant to the requested judgment; tests only where applicable

Completion report:
1. answer or scoped verdict
2. supporting findings and uncertainty
3. remaining decision or next action, if any
```

## Pattern: Documentation-Only Task

Use for a requested document or revision, including an existing Word or other
project-owned format. Harness policy edits remain repository maintenance and
retain their required checks.

```text
Goal:
Write or revise [document and requested result] using [existing format/source].

Scope:
[Requested document or sections; protected originals and content to preserve.]

Decisions:
[Applicable user decisions; genuinely missing decisions affecting this output.]

Checks:
- requested content and format
- source support and consistency with applicable decisions
- current unresolved items, separately from later finalization
- additional checks required by the target policy or changed automation

Result:
Deliver the document, a concise change summary, checks, and remaining decisions.
```

Do not add STATUS, acceptance records, JSON packages, executable tests, or a new
authoring pipeline solely because the task produces a document. Create or
update those only when the requested scope or applicable policy requires them.

## Pattern: Downstream Feedback Capture

Use when a downstream experiment should be summarized at template level.

```text
Goal:
Capture downstream feedback without copying downstream source content.

Source:
Separate downstream target, path generalized in docs.

Allowed content:
- document type
- source row identifier
- PASS/PARTIAL/BLOCKED result
- generalized finding

Forbidden content:
- raw source bulk copy
- sensitive requirement text
- live value or connection detail
- implementation code

Completion report:
1. feedback record
2. source-use result
3. prohibited content check
4. template-level recommendation
```

## Pattern: Downstream Practical Probe Retrospective

Use after a downstream repository practical probe. Default mode is review-only.
The purpose is to decide whether completed downstream probe evidence justifies
no `codex-dev-harness` change, a minimal docs-only improvement, or deferral
until more downstream evidence exists.

This pattern does not collect downstream domain evidence, approve
implementation, or add automation. Target repositories remain governed by their
own `AGENTS.md` or equivalent repo-local rules. `codex-dev-harness` remains
frozen unless repeated downstream evidence justifies a small documentation-only
change.

```text
Goal:
Review completed downstream practical probe results and decide whether they
justify a minimal codex-dev-harness improvement, no change, or deferral.

Source:
- downstream repository name
- probe commit hashes or closeout records
- changed files summary
- verification and safety results
- any friction or failure patterns

Write scope:
Read-only by default. Do not edit files unless a separate docs-only patch is
explicitly approved.

Review criteria:
- Did the task contract work?
- Did read-order and repo-local rules work?
- Did allowed-file and forbidden-action scoping prevent drift?
- Did verification reporting work?
- Did closeout evidence capture safety boundaries?
- Did Code Simplicity guidance help keep the probe small?
- Was any friction repeated enough to justify a small harness change?
- Is no change the better outcome?

Improvement options:
- no change
- minimal docs-only prompt/policy wording
- defer until another downstream probe
- reject automation/profile/example expansion unless separately justified

Forbidden actions:
- no downstream repo edits
- no downstream domain evidence collection
- no runtime code
- no CI workflow
- no RAG/index/vector store
- no audit automation
- no eval quality-gate integration
- no release artifact generation
- no tag movement
- no new profile or example
- no implementation approval
- no Hermes/MCP/runtime-agent expansion

Completion report:
1. PASS/PASS WITH NOTES/BLOCKED summary
2. downstream probe summary
3. what worked
4. friction observed
5. harness implications
6. improvement options considered
7. recommendation: no change / minimal docs-only patch / defer
8. exact allowed files for any future patch
9. forbidden actions
10. next step
```

## Pattern: Release/Closeout Task

Use when recording release or phase evidence.

```text
Goal:
Record closeout for [phase/tag/decision].

Required evidence:
- basis commit or tag if applicable
- commands run
- PASS/FAIL/NOT RUN result
- scope exclusions

Forbidden actions:
- no tag movement unless explicitly requested
- no release publication unless explicitly requested
- no workflow creation

Completion report:
1. evidence recorded
2. verification result
3. excluded actions confirmed
4. next decision
```

## Prohibited Prompt Content

Do not include:

- raw private source content
- sensitive requirement text
- IP, port, tag value, or live parameter value
- secret, token, credential, account, private input, or live config value
- equipment connection detail
- approval-free live/device/runtime work request

## Prompt Review Checklist

- Goal is concrete.
- Target path is explicit.
- Write scope is explicit.
- Allowed files are narrow.
- Forbidden actions are explicit.
- Necessary checks are identified; executable commands are listed only when applicable.
- Completion report format is specified.
- Side effects require explicit approval.
- Prompt templates do not authorize side effects; they only make the requested
  boundary easier to review.
