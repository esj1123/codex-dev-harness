# Review perspectives

Choose questions relevant to the requested judgment, design stage and affected
relationships. This is an open set of perspectives, not a universal checklist.
Project acceptance criteria and actual technical sources govern each conclusion.

| Perspective | Questions worth resolving when applicable | Evidence to inspect |
|---|---|---|
| Requirements and completeness | Is the required behavior covered? Are conditions, responsibilities and acceptance criteria clear and mutually consistent? | Current requirements, allocation and scoped decisions |
| Function, behavior and logic | Do states, sequences, modes, timing and abnormal paths produce the stated behavior? | Design descriptions, logic/state models and relevant implementation or test evidence |
| Interfaces and consistency | Do both sides agree on identity, direction, units, format, timing and ownership? | Interface definitions and related lists, diagrams and specifications |
| Calculation, selection and allocation | Are inputs, units, aggregation, formulas, rounding and applicable constraints sound? Are assignments complete and valid? | Input items and actual project criteria, calculations and allocated outputs |
| Physical realization | Can the selected arrangement meet the applicable envelope, access, routing and assembly constraints? | Dimensions, layout and relevant equipment or installation information |
| Performance, safety and reliability | Are the required limits, margins, failure assumptions and mitigations supported? | Applicable project criteria, analyses and relevant evidence; do not invent universal thresholds |
| Operations and maintenance | Are prerequisites, sequence, access, abnormal response and recovery supported by the current design? | Operating/maintenance procedures, configuration and limits |
| Verification and testability | Can the method demonstrate the stated criterion? Are prerequisites and observations sufficient, and plans distinct from results? | Requirement links, methods, procedures, acceptance criteria and actual test records |
| Traceability and change impact | Is the decision based on the correct source/revision? Has its effect reached the required authorized outputs? | Existing IDs, revision records, decisions, actual candidate changes and dependencies |

## Scope findings to the actual claim

Check semantic correctness separately from formatting, file integrity and native
application behavior. A readable PDF does not prove editable CAD objects, and a
consistent set of documents does not prove the shared design is correct.

For an incomplete basis, identify the specific unsupported conclusion and the
missing input or decision. Continue supported review. Apply stage-appropriate
criteria and carry existing scoped provisional approvals; later finalization is
not automatically a present defect.

## Synthetic boundary examples

| Situation | Review focus |
|---|---|
| A requirement and interface table use different units for the same exchange. | Resolve against the applicable source; point to the inconsistent items and affected calculations rather than silently selecting one. |
| A preliminary design explicitly reserves a numeric choice for the next stage. | Check whether the present conclusion is supported under the approved assumption; do not demand unrelated final-stage evidence. |
| All outputs copy one incorrect calculation. | Re-evaluate the affected derivation from input and criteria before comparing transcription. |
| A test procedure contains expected results but no execution evidence. | Review its adequacy as a plan; do not report that the test passed. |
| A routine wording change leaves meaning and dependencies intact. | Review the changed text and relevant references without imposing all perspectives. |

Examples supply no real project data or approval and do not require creation of
a register, test harness or additional documents.
