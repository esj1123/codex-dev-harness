# Prompt Patterns

## Purpose

Provide reusable prompt patterns for Codex work requests as clear task contracts.

These patterns are documentation-only. They do not execute tasks, grant side-effect approval, create runtime code, or bypass project safety policies.

## Reusable Prompt Template Files

Use these files as copy-ready prompt contracts when a task needs more structure
than the short patterns below:

| template | use when |
|---|---|
| `prompts/task_contract/task_contract.md` | requesting scoped implementation, documentation, review, or verification work |
| `prompts/task_contract/critic_review.md` | requesting review-only correctness, safety, scope, and evidence review |
| `prompts/task_contract/verification_closeout.md` | recording changed files, commands, evidence, safety checks, risks, and next step |
| `prompts/task_contract/release_summary.md` | summarizing release state without creating tags, moving tags, publishing, or generating artifacts |

These prompt templates do not grant approval by themselves.

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
- verification commands
- completion report format
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

Use when no files should be changed.

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
- missing tests or evidence

Completion report:
1. PASS/PARTIAL/BLOCKED summary
2. findings
3. risks
4. recommended next steps
```

## Pattern: Documentation-Only Task

Use when only Markdown or policy records should change.

```text
Goal:
Document [decision/plan/record].

Allowed files:
- docs/[file].md
- STATUS.md
- ACCEPTANCE_TRACE.md

Forbidden files/actions:
- no runtime code
- no render/gate/example integration
- no workflow creation

Verification:
- documentation presence check
- quality gate if available

Completion report:
1. created/updated files
2. summary
3. verification result
4. remaining decisions
```

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
- Verification commands are listed.
- Completion report format is specified.
- Side effects require explicit approval.
- Prompt templates do not authorize side effects; they only make the requested
  boundary easier to review.
