# Document families

Read the rows relevant to the requested deliverable. This is an extensible guide
to content decisions, not a mandatory set of documents or checks. Existing project
definitions, templates, sources and explicit decisions determine the result.

| Family | Authoring focus | Evidence and affected relationships |
|---|---|---|
| Requirements and specifications | Scope, conditions, measurable criteria, IDs and allocated responsibilities | Upper-level requirements, constraints, decisions, interfaces and verification intent |
| System, hardware and software design | Architecture, functions, behavior, selected configurations and rationale | Requirements, interface definitions, analyses and relevant implementation constraints |
| Interfaces and connections | Boundaries, endpoints, directions, units, states and exchanged information | Definitions on both sides, signal or data identities and related drawings |
| Input data, lists and calculations | Quantity basis, units, formulas, selection and allocation | Source rows and revisions, applicable design criteria, output lists and drawings |
| Drawings and diagrams | Objects, dimensions, layout, connectivity, symbols and references | Controlling design decisions and editable native objects; use diagram guidance when needed |
| Test and verification documents | Objective, prerequisites, actions, expected results, acceptance criteria and observed evidence | Requirements and testability; keep planned actions separate from actual results |
| Operations, maintenance and change records | Preconditions, sequence, abnormal response, recovery, maintenance and change effects | Current configuration, operating limits and authorized changes; do not invent live values |

A document may span families. A project-specific deliverable outside this table
still uses its own purpose, readers, required decisions and available evidence;
do not ask the user to rename it or create an empty specialization.

## Stage and status

At a preliminary stage, preserve explicit assumptions and approved provisional
choices while supporting the conclusions actually required now. At a detailed
stage, resolve the identities and interfaces required for the requested detail.
For as-built or results documents, use observed configuration or execution
evidence; a plan is not evidence that construction or testing occurred.

These are selection principles, not universal stage gates. Apply the project's
actual acceptance criteria. An item reserved for later does not block unrelated
current work, while a missing premise needed for the current conclusion remains
unresolved. Reuse current scoped decisions rather than asking again solely
because a marker says TBD or TBC.
