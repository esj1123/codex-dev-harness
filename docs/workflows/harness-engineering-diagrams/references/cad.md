# CAD work

Read when the requested artifact is CAD or a CAD-specific limitation matters.
Use the user's chosen native format and verified available tools; these
instructions neither install a tool nor establish its license or API readiness.

## Preserve the affected native structure

Resolve the selected drawing revision, sheet/layout and design basis. Reuse the
existing title block, symbols, layer conventions, units, scale and dimensions.
Inspect block definitions, insertions and attributes where they carry changed
identities. Account for relevant external references, fonts, plot settings,
embedded objects and custom/proxy objects when their preservation affects the
requested edit or output. Do not audit all dependencies for a bounded title edit.

Use object identity and native connection information where available; coincident
lines and text are not proof of semantic electrical connectivity. Preserve
unaffected objects and references. A flattened preview placed inside a CAD file
does not meet a requirement for editable objects.

## Relate the drawing to the design

Compare changed quantities, placements, labels and connections with their
controlling lists, calculations or design decisions. Use existing identifiers to
follow relationships. When a physical constraint changes the design, return it
to the applicable decision authority and carry the accepted change into the
authorized outputs; do not silently rewrite input data to fit a drawing.

## Choose a bounded editing route

Prefer an available native route that can preserve the affected objects. Select
an alternative only after identifying its actual limitation for this artifact.
Do not treat a generic DXF parser as a native DWG editor, or successful conversion
as proof that custom objects, fonts, dimensions or connection semantics survived.
If conversion or repair is authorized, use designated working copies, preserve
the original, and check affected semantics and appearance. An audit/repair option
can change objects and is not merely read-only inspection.

## Report what was observed

Separate design/content checks, visual checks, native object inspection and
save/reopen observations. Use native open/save/reopen only when necessary for the
requested result and within scope. A preview can support appearance review;
it does not prove native editability or preservation after saving.

If the source, tool or required identity is unavailable, finish supported
preparation and specify the unedited or unverified portion. Do not claim a native
result, silently substitute a different final format, or block unrelated work.
