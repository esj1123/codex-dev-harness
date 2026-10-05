# Synthetic examples

These examples illustrate decisions, not real equipment or mandated tooling.

| Request and evidence | Appropriate response |
|---|---|
| Move two blocks on page 2 of an editable Visio drawing without changing their connections. | Preserve object identities, endpoints, and direction; reuse the frame and symbols. Check moved blocks, connected lines, labels, and affected cross-page references. |
| Add an interface whose source names both endpoints but leaves its direction undecided. | Preserve the two identities and identify the direction decision; do not infer an arrow from layout. Continue unaffected arrangement. |
| An SVG preview looks correct, but no native Visio open/save/reopen was observed. | Report visual preparation or review only. Native editability and save/reopen remain unverified. |
| The user requests native editable shapes, and the available export only embeds a single flattened image. | Explain the format limitation and prepare what is useful; do not claim editable engineering objects or silently change the requested deliverable. |
| Update a weekly report's ordinary progress chart. | Use the report/chart workflow; engineering topology guidance is unnecessary. |
| Correct a CAD title block without changing quantities or connections. | Edit the affected title/revision fields and inspect their appearance; do not audit every circuit or recalculate hardware. |
| A CAD layout shows that the selected configuration cannot fit the allowed envelope. | Identify the actual constraint and decision, resolve it through project authority, then propagate the accepted change only within authorized outputs. |
