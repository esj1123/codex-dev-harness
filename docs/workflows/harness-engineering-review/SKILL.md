---
name: harness-engineering-review
description: "Review engineering requirements, designs, interfaces, calculations, data lists, drawings, test or operating documents and their relationships. Use for technical adequacy, source support, design decisions or change impact, including cross-document review. Ordinary prose, code/security review and authoring-only requests keep their existing workflows."
---

# Engineering review

Answer the requested engineering judgment from the actual target, applicable
sources and project criteria. This is a review role, not another universal gate
or permission to edit. It applies beyond electrical, I/O and CAD work.

## Select the question and evidence

Read the project's work-guidance entrypoint (such as README or AGENTS) first when
present, and give the rules and decisions it points to precedence over this skill.
Establish the requested result, affected items and revisions, document purpose,
design stage, and current acceptance criteria from existing context. Infer the
appropriate review; do not ask the user to classify routine work or complete a
new form. Ask only for a missing decision that materially changes the judgment.

Read [review perspectives](references/review-perspectives.md) for the technical
questions that apply. Choose by the actual change and its dependencies; do not
run all perspectives or whole-project tests on every document. Preserve project
required checks and expand for a concrete gap, contradiction or failure.

## Check the basis as well as the result

Inspect the original relevant inputs, applicable rules and actual candidate.
Establish authority per fact or decision, using project sources and revisions;
neither a format nor a writer's summary makes data authoritative. Check derived
results from their input basis where needed, and then their reflection in related
artifacts. Several agreeing outputs can share the same calculation or copying
error. Do not approve solely from the author's self-check or generated assertions.

Preserve approved provisional decisions in their scope and distinguish current
prerequisites from later finalization. Do not demand detailed-design or as-built
evidence merely because a preliminary document has a visible future item. Missing
evidence needed for the current conclusion remains unresolved. Do not invent a
technical limit or treat a plan as observed implementation or test execution.

Follow relevant feedback as well as forward derivation: a layout, analysis or
test can reveal a constraint requiring an upstream design decision. Identify the
affected source/decision and dependent outputs, including out-of-scope updates.
Do not silently choose a new authority or synchronize conflicting originals.

## Use specialized references only when needed

When installed, these sibling references can clarify a relevant context:

- [Document families](../harness-engineering-documents/references/document-families.md): unfamiliar deliverable or stage expectations.
- [Design derivation](../harness-engineering-documents/references/design-derivation.md): calculation, selection, allocation or cross-document changes.
- [Electrical/I/O](../harness-engineering-documents/references/electrical-io.md): electrical identities and allocation relationships.
- [CAD](../harness-engineering-diagrams/references/cad.md): native objects, drawing dependencies and evidence limits.

These are conditional guidance, not project technical authority or a requirement
to install the authoring skills. If a sibling reference is absent, use this
skill's review method and the available project sources. State only the actual
evidence gap affecting a judgment; do not fail the whole review for the missing
optional reference. Do not load authoring instructions as permission to write.

## Report and connect corrections

Report the conclusion for the reviewed scope, actionable findings with location,
source/criterion, impact and correction direction, and necessary unverified
coverage. Separate mandatory defects from optional improvements. Use the existing
review medium; a new report file or formal PASS/FAIL label is not always needed.
With incomplete coverage, qualify the conclusion instead of asserting total
correctness or rejecting unrelated supported work.

Keep a review-only request read-only. If the user already requested review and
correction, hand findings into an explicit authoring phase within the authorized
write scope without re-asking for the same permission. Preserve protected inputs
and recheck corrected findings and their impact; do not repeat completed review
without a relevant change or new concern.

Author self-checks remain useful but are distinct from independent review. Use
independence when requested, required by the project or warranted by material
design risk (for example, changes affecting procurement quantities, external
interfaces, or safety/operating limits); do not spawn another reviewer for every
minor edit. These are examples, not a closed list; a stage name alone neither
requires nor exempts independent review. A claim of
independent review requires a separate reviewer examining the candidate and
necessary original evidence, not a second label on the author's own check.
