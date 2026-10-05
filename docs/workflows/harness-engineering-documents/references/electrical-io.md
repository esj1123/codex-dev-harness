# Electrical and I/O relationships

Use only for work linking input quantities, I/O identities, hardware allocation,
layouts, connection drawings or wiring tables. This is generic guidance; project
sources supply all real equipment specifications, formulas, limits and decisions.
It is one domain example, not a required model for other engineering documents.

## Quantities to configuration and layout

Locate the source quantities and classification used by the design. Resolve the
applicable module capacities, usable slots, grouping, reserve, redundancy or
separation criteria only where the project requires them. Do not assume a spare
percentage, module type, chassis size or universal rounding formula.

Follow quantities through the actual module and chassis allocation into the
layout. Check affected identities and assignments as well as counts: a matching
chassis total can conceal an unassigned group or a duplicate device. More input
points do not automatically require another chassis if the applicable allocation
has capacity; determine that from the actual criteria and configuration.

## I/O identities to connections and wiring

Use existing signal, equipment, module/channel, terminal, connector, cable/core
and drawing references where applicable. Identify the relationship used by the
project rather than requiring every field in every source.

For a changed signal, follow its affected endpoints and assignments into the
connection drawing and detailed wiring record. That record may be a spreadsheet
or drawing. Check omissions, unintended duplicates, conflicting direction or
endpoint identity, and affected cross-sheet references. Preserve permitted
shared connections; do not interpret every repeated identifier as an error.

Visible line/text proximity does not establish a native electrical connection.
Read actual attributes or supported native semantics where the requested result
requires them; state the limit when only a plotted image is available.

## Feedback and synthetic examples

| Synthetic situation | Appropriate treatment |
|---|---|
| Input counts are known, but applicable reserve and usable-slot criteria are absent. | Complete supported aggregation; identify which missing criteria prevent a final configuration instead of inventing them. |
| A signal endpoint changes in the I/O list. | Trace the affected drawing and wiring entries, update authorized outputs, and name any required out-of-scope change. |
| A chassis does not fit the available layout envelope. | Resolve the configuration or arrangement decision from the actual constraints, then update affected authorized calculations and outputs. |
| A calculation and two drawings show the same chassis count. | Check the input-based allocation as well as agreement; common copying can preserve one error. |

These examples contain no project technical values and grant no source editing,
native application use, equipment access or approval.
