---
name: harness-engineering-diagrams
description: "Create or revise engineering layouts, block, interface, system, process, connection, or logic drawings whose objects, dimensions or connections matter, including editable CAD and Visio files. Use for drawing changes in existing frames and conventions. Use review guidance for review-only requests; decorative images, ordinary charts and document-only prose keep their own workflows."
---

# Engineering diagrams

Deliver the requested drawing in the user's chosen editable format. Project
sources and decisions establish engineering meaning; this skill guides the
change and does not supply equipment facts or authorize native/device actions.

## Establish the drawing change

Read the project's work-guidance entrypoint (such as README or AGENTS) first when
present, and give the rules and decisions it points to precedence over this skill.
Read the affected page, object identities, connections, and current source or
decision that supports the change. Reuse known facts before asking questions.
Identify a missing decision only when it changes topology, output, or the allowed
action. Keep independent layout work moving when that decision does not affect it.

Reuse the existing frame, title block, revision convention, legend, symbols, and
components. Distinguish working-file versions (for example, v1-v9) from formal
document revisions and issue stages (for example, Rev A, IDC -> IFR -> IFC);
follow project meanings and sequencing, and preserve earlier working versions.
Follow the user's selected tool and native format. Propose a different
method only when a material limitation requires a choice. Do not build an icon
library, generator, or converter as an automatic precondition to a drawing edit.

For CAD work, read [CAD guidance](references/cad.md) for the affected native
objects and file dependencies. Read only the relevant drawing or format detail;
a title-block edit does not require auditing every electrical connection.

## Preserve engineering meaning

Resolve which objects and connections change before arranging them visually.
Preserve unaffected identities, connector endpoints and direction, labels, and
cross-page references. Do not invent quantities, specifications, or connections;
retain visible uncertainty under the project's convention. Carry forward approved
provisional decisions within their scope, while resolving contradictory evidence
or current-stage prerequisites for the affected change.

Check technical correctness separately from presentation. A tidy preview cannot
prove endpoint connectivity; a technically correct drawing may still need
readable labels, spacing, alignment, line routing, and an updated affected legend.

Quantities and allocations can originate in calculations, lists or design
decisions. Check affected identities against those sources, not only visible
counts. If the drawing reveals a physical or interface constraint that changes
the design, return it to the project's decision authority and update related
authorized outputs after the decision is resolved. Do not silently alter input
values to fit the drawing or overwrite protected sources.

## Produce and verify the requested artifact

Edit the native source using available, appropriate tools. Keep objects and
connectors editable when the user requests native editability. A flattened image
embedded in a native container is not equivalent. SVG/PNG/PDF previews can help
review appearance but do not establish native Visio editing, save/reopen behavior,
or connector semantics.

Check changed pages, objects, connections, and affected legends or references.
Use native open/save/reopen checks when they are necessary for the requested
result and authorized; expand scope only for a relevant dependency or failure.
Do not run unrelated code tests or audit every drawing by default.

When a native tool, editable source, or required identity is unavailable, finish
useful authorized preparation and state the exact gap. Label a plan or preview as
such. Do not claim a native file or runtime behavior was verified without observing
it, and do not substitute a different final format without the user's decision.

## Return the result

Identify the changed drawing/pages, technical and visual checks actually completed,
native editing evidence when required, and any remaining decision. Separate
prepared, edited, and verified states in plain language. Avoid new sidecar records
unless requested or required by the project.

Read [synthetic examples](references/examples.md) only when a boundary is unclear;
the examples are not engineering source evidence.
