---
name: harness-engineering-documents
description: "Author or revise engineering documents, including requirements, designs, interfaces, calculations, data lists, test procedures, and operating or change records. Use for engineering content, design derivation, selection or allocation, and coordinated document updates. Use review guidance for review-only requests and diagram guidance for drawing-only edits; ordinary reports, simple prose, and coding keep their own workflows."
---

# Engineering documents

Deliver the document change the user requested in the existing project format.
Use this skill for engineering content decisions; use the relevant document or
spreadsheet tool instructions for file editing and rendering. Project authority,
the user's scope, and explicit decisions govern the work.

## Start with the intended result

Read the project's work-guidance entrypoint (such as README or AGENTS) first when
present, and give the rules and decisions it points to precedence over this skill.
Read the affected document, applicable format, source references, and latest
decisions. State the intended change briefly using facts already available.
Reuse the user's chosen authoring approach. Ask only about a missing decision
that materially changes the result or prevents an authorized change; continue
independent work while it is unresolved. Do not ask the user to complete a new
workflow form or choose among equivalent implementation methods.

Resolve the current revision and document of record before editing. Keep working-file
versions separate from formal revisions and issue stages, following project meanings
and order while preserving earlier working versions. Preserve
unrelated changes, identifiers, tables, cross-references, and protected sources.
Work in the existing document or designated candidate. Create a companion
register, schema, converter, or authoring pipeline only when requested.

Select details from the actual document purpose, design stage, and requested
change. Read [document families](references/document-families.md) when the
deliverable's content or evidence needs clarification; its families are examples,
not a closed catalog. Project definitions govern codes such as HDS, SDS or DAT.
A bounded wording or table edit does not require a design derivation workflow.

## Derive and carry related design changes

For calculations, selection, allocation, or changes spanning artifacts, read
[design derivation](references/design-derivation.md). Establish the controlling
source and revision for each affected fact or decision; a file format alone does
not make all of its contents authoritative. Derive results from available project
criteria and retain unresolved criteria visibly instead of supplying defaults.

Update the affected authorized documents together using their existing IDs and
references. A layout or implementation constraint can require revisiting an
upstream decision: follow the project's decision authority, then propagate the
accepted change. Preserve protected sources and name necessary changes outside
the write scope without editing them or claiming overall consistency.

Use [electrical and I/O relationships](references/electrical-io.md) only for that
domain. It supplies neither project equipment facts nor a universal data model.
Use available diagram or file-format guidance only for the outputs that need it;
do not load all specializations for every task.

## Carry decisions into the document

Distinguish confirmed facts, explicitly approved provisional content, and items
reserved for later finalization. Reuse approval for the same target, action, and
scope. A TBD/TBC marker alone does not invalidate current approval or reopen a
settled choice. Missing evidence required for the current acceptance stage,
contradictions, or a material scope change remain reasons to resolve the affected
item; explain the exact dependency rather than holding the whole document.

Write unknown values as unknown. Do not infer equipment identity, quantities,
interfaces, compliance, or completed tests from a convenient example. Keep
planned verification separate from an observed result. Preserve existing source
and revision conventions rather than introducing a second tracking system.

## Edit and check the affected content

Apply the requested text, table, or requirement change first. Review its meaning,
source support, IDs, references, and directly affected sections. Check layout
where the output format or changed content requires it. Follow required project
checks, and expand further only for a specific dependency, contradiction, or
failure. A local wording edit does not itself require code tests, a new test
harness, or a whole-project audit.

Check both the derivation and its transcription where calculations or allocation
changed. Matching values in several outputs do not prove the shared result is
correct. Keep author self-checks distinct from independent review: request or
perform independent review when the user's scope, project rules, or material
design risk (for example, changes affecting procurement quantities, external
interfaces, or safety/operating limits) calls for it, without adding it to every
minor edit. These are examples, not a closed list; a stage name alone neither
requires nor exempts independent review. Review findings
may be repaired under an existing request covering review and correction; a
review-only request provides no editing permission.

Use the requested editable format and the existing template.
For existing Office templates and formatted documents, start by changing only
the affected package parts (for example, the edited worksheet XML) instead of
rewriting the whole package with a general-purpose library, and treat any lost
headers, images or other parts as defects.
Verify preservation by comparing internal parts against the original, with only
intended parts differing and previews serving as supporting evidence.
If the required
source or native tool is unavailable, complete the useful authorized preparation
and identify exactly what remains unedited or unverified. Do not present a text
draft, exported preview, or static check as a verified native document.

## Return the result

Report the changed document and affected sections, the checks actually performed,
and only the remaining decisions needed for the current result. Keep later
finalization items distinct. Do not add a separate receipt or checklist unless
the task or applicable policy requires it.

Read [synthetic examples](references/examples.md) only when a boundary is unclear;
the examples supply no project facts or approval.
