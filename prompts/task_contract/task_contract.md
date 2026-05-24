# Task Contract Prompt

Use this prompt when requesting AI/Codex implementation, documentation, review, or verification work.

This template is documentation-only. It does not grant approval for side effects, execute automation, or override repository policy.

## Goal

[Describe the concrete outcome required.]

## Target Repo / Path

- Repository: [repo name or URL]
- Local path: [absolute or repo-relative path]
- Basis ref or commit, if relevant: [branch, tag, or commit]

## Write Scope

Choose one:

- Read-only. Do not edit files.
- Documentation-only writes.
- Code/test writes within the allowed files below.
- Other: [describe and require explicit approval]

## Allowed Files

- [file or directory]
- [file or directory]

## Forbidden Files / Actions

- Do not edit files outside the allowed list.
- Do not perform unrelated refactors.
- Do not delete, move, overwrite, or force-write files unless separately approved.
- Do not create or modify CI workflows unless separately approved.
- Do not generate release artifacts unless separately approved.
- Do not add eval, audit logging, RAG, application, device, or live-write behavior unless separately approved.
- Do not include secrets, private raw input, sensitive source text, equipment details, live parameters, or credentials.

## Verification Commands

Run when safe and available:

- [command]
- [command]

If a command is not run, report `NOT RUN` or `ENVIRONMENT BLOCKED` with the reason.

## Side-Effect Approval Boundary

The following actions require separate explicit human approval before execution:

- external sends, messages, notifications, or publication
- deletion, move, overwrite, force, or broad filesystem changes
- dependency installation or environment mutation outside the requested scope
- tag creation, tag movement, release publication, manifest/checksum/SBOM/provenance generation
- workflow installation or external service changes
- database mutation, live target mutation, PLC/device write, start, stop, reset, or mode change

## Completion Report Format

1. Files changed
2. Behavior or document summary
3. Verification result
4. Safety checks
5. Unresolved risks or assumptions
6. Recommended next step
