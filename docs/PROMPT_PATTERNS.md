# Prompt Patterns

## Purpose

Provide reusable prompt patterns for Codex work requests as clear task contracts.

These patterns are documentation-only. They do not execute tasks, grant side-effect approval, create runtime code, or bypass project safety policies.

## Basic Task Contract Structure

A well-scoped Codex task should state:

- goal
- target repo or path
- read-only vs write scope
- allowed files
- forbidden files or actions
- verification commands
- completion report format

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
4. known risks
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
