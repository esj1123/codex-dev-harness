# Human Approvals

## Purpose

Define what counts as human approval for codex-dev-harness work and which actions require separate approval.

This policy is documentation-only. It does not grant approval for any current or future side effect.

## Approval Principle

Approval must be explicit, scoped, and tied to a concrete action.

A valid approval should identify:

- requested action
- target repository, file, branch, tag, system, or external surface
- allowed scope
- forbidden actions
- whether the approval is one-time or part of the current task only
- verification or closeout expectations

Broad statements such as "continue", "make it better", or "handle it" do not approve high-risk side effects unless the requested action and target are already concrete and in scope.

## Approval Required

Separate explicit approval is required before:

- deleting, moving, or overwriting files outside the requested scope
- using `--force` or equivalent overwrite behavior
- creating or modifying profiles
- adding examples
- installing GitHub Actions workflows
- publishing GitHub Releases
- creating, moving, or signing tags
- creating release manifests, checksums, SBOMs, or provenance artifacts
- implementing an eval harness
- expanding an approved corpus for retrieval or RAG use
- creating retrieval indexes, embeddings, vector stores, or RAG tooling
- adopting a model or prompt change for a governed workflow
- adding dependencies beyond the approved task
- changing external services or APIs
- sending email, messages, or notifications
- mutating databases
- adding live target write behavior
- adding PLC/device write, start, stop, reset, or mode-change behavior

## Approval Not Sufficient

Even with approval, this repository baseline must not receive:

- real application code
- C# source, solution, project, XAML, or build assets
- PLC/device code
- secrets, credentials, tokens, or private input
- raw source bundles or sensitive source text
- equipment IPs, ports, tags, or live parameter values

Those remain out of scope unless a separate future repository direction explicitly changes the product boundary.

## Approval Records

Record approval-sensitive decisions in the nearest relevant surface:

- `templates/base/APPROVALS.md.template` for downstream generated projects
- `STATUS.md` for repository state
- `ACCEPTANCE_TRACE.md` for requirement-to-evidence mapping
- dedicated decision or closeout docs under `docs/` when the decision is durable

Do not record secrets, private raw input, equipment details, or live values in approval records.

## Approval Identifiers

Future audit evidence may reference an `approval_id`. An approval identifier is
a pointer to an approved decision record, not the approval content itself.

An `approval_id` should be:

- scoped to the task or decision
- stable enough to cite from future evidence
- connected to a record in `STATUS.md`, `ACCEPTANCE_TRACE.md`, a dedicated
  decision or closeout document, or a downstream `APPROVALS.md`
- free of secrets, private input, raw source, equipment details, live values,
  and personal data beyond the approved evidence label

Recording an `approval_id` does not grant new approval. It only references an
approval that was already explicit and scoped.

## Model And Corpus Approval Records

Approved-corpus expansion and model or prompt changes should be recorded before
implementation or adoption.

Approval records should identify:

- exact corpus files, directories, or patterns
- forbidden corpus material
- model or prompt identifiers when applicable
- eval or closeout evidence expectations
- approved side-effect class
- residual risks

Do not record raw prompts, model outputs, private input, raw source, live
configuration, equipment details, secrets, or live values in approval records.

## Revocation And Expiry

Approval is task-local unless stated otherwise. A later task must re-establish approval for new side effects, changed targets, or broader scope.

## Non-Goals

This policy does not create an approval workflow engine, identity system, audit database, or automation hook. It defines documentation-level approval rules only.
