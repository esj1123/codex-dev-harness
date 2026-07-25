# Greenfield Local Data Quality CLI Target Contract

## Purpose

Select a low-risk greenfield target for the first controlled harness
application. This contract fixes the intended product boundary, future command
surface, render profile, render tier, and safety constraints before any target
repository is created or any application code is implemented.

This task is contract-only. It does not create, inspect, initialize, render
into, or implement the selected target.

## Allowed Files

This task may add only:

- `docs/GREENFIELD_LOCAL_DATA_QUALITY_CLI_TARGET_CONTRACT.md`
- `tests/test_greenfield_local_data_quality_cli_target_contract.py`

It must not modify `STATUS.md`, `ACCEPTANCE_TRACE.md`,
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, scripts, templates, examples,
schemas, gates, workflows, artifacts, release evidence, or corpus membership.

## Basis

The candidate is a new local-only utility with no legacy authority files,
private inputs, downstream dependencies, network boundary, or live target. The
owner-selected target path was absent when this contract was established. The
absolute path is intentionally not recorded, and this task does not create it.

The existing render-tier contract defines `python_cli` with `standard` as a
14-document profiled surface. That surface provides project, boundary, data,
approval, phase, status, acceptance, safety, and verification records without
the full tier's source inventory and profile README.

## Candidate Decision

```text
Decision: greenfield_local_data_quality_cli_target_selected_without_repository_creation_or_implementation
Status: CONTRACT_ONLY
Target alias: local-data-quality-cli
Runtime profile: python_cli
Render tier: standard
Rendered file count: 14
```

The safe alias identifies the candidate for planning only. It is not a
repository identifier, filesystem location, approval reference, or authority
to create or access a target.

## Product Contract

Version 1 is a local CSV data-quality command-line utility. It reads one CSV
file and one JSON rules file, performs bounded validation, and reports only
aggregate quality results to stdout.

The checks are:

- required-column presence;
- empty values in configured non-empty columns;
- duplicate non-empty values in configured unique columns;
- numeric conversion failures in configured numeric columns; and
- input data-row and column counts.

The tool does not modify the CSV or rules input.

## Future CLI

The future public command is fixed as:

```text
python -m local_data_quality_cli \
  --input <CSV_PATH> \
  --rules <RULES_JSON> \
  [--json]
```

`--input` and `--rules` are required. `--json` selects structured stdout.
There is no output-path option, write option, recursive-directory option, or
stdin mode in version 1. This contract does not implement or execute the
command.

## CSV Input Contract

The input must be one regular CSV file with all of these properties:

- encoding is UTF-8 or UTF-8 with BOM;
- delimiter is a comma;
- exactly one header row appears first;
- header names are non-empty and unique;
- the file is no larger than 10 MiB;
- there are no more than 100,000 data rows;
- there are no more than 256 columns; and
- every data row has the same field count as the header.

Malformed CSV, an empty input, a missing header, duplicate or empty header
names, or a row-width mismatch is a `FAIL`.

## JSON Rules Contract

The rules input must be one regular UTF-8 JSON object with exactly these keys:

- `schema_version`
- `required_columns`
- `non_empty_columns`
- `unique_columns`
- `numeric_columns`

`schema_version` must be the string `"1"`. Each column-list field must be a
list of unique, non-empty strings and may contain no more than 64 columns.
Unknown keys, missing keys, duplicate entries, or incorrect types make the
rules malformed and produce `FAIL`.

Every configured rule column must exist in the CSV header. `unique_columns`
defines independent per-column uniqueness. Composite keys and cross-column
uniqueness are not part of version 1.

## Validation Semantics

- Required columns are checked against the decoded header before data rows are
  evaluated.
- A value is empty when trimming surrounding whitespace leaves an empty
  string.
- For each `unique_columns` entry, repeated non-empty decoded values after the
  first occurrence count as duplicate violations for that column. Empty values
  are excluded from uniqueness counting.
- Numeric validation trims whitespace and applies standard-library decimal
  parsing. Non-finite values are rejected. Empty values are excluded from
  numeric parsing and are reported only when the same column is also listed in
  `non_empty_columns`.
- Results contain aggregate counts only. No source value is retained or
  emitted.

## Output Contract

Default stdout is one bounded summary line. With `--json`, stdout is a
deterministic JSON object with sorted keys and exactly one final newline. The
complete output must not exceed 8 KiB.

The JSON top-level fields are exactly:

- `schema_version`
- `tool_id`
- `status`
- `reason_codes`
- `input_summary`
- `rule_summary`
- `issue_summary`
- `performed_actions`

`schema_version` is `"1"` and `tool_id` is `local_data_quality_cli`.
`input_summary` contains only row count, column count, and detected encoding.
`rule_summary` contains only configured rule counts by class. `issue_summary`
contains only counts for missing columns, empty values, duplicate values, and
numeric conversion failures. `performed_actions` is always `[]`.

Plain and JSON output must not contain raw rows, cell values, absolute paths,
input filenames, the rules source text, tokens, credentials, secret-like
values, private data, customer data, or live values. No report, artifact,
receipt, trace, or audit file is persisted.

## Status And Exit Codes

Status priority and process exit codes are:

1. `NOT RUN`: required CLI arguments are missing or CLI usage is invalid;
   exit `2`.
2. `ENVIRONMENT BLOCKED`: an input cannot be opened or its encoding cannot be
   read in the local environment; exit `1`.
3. `FAIL`: CSV or rules are malformed, a configured column is missing, or any
   data-quality violation is present; exit `1`.
4. `PASS`: both inputs are valid and no violation is present; exit `0`.

No status authorizes a write, external action, or later phase.

## Render Contract

The future repository initialization candidate uses:

- runtime profile: `python_cli`;
- render tier: `standard`; and
- exact rendered file count: `14`.

The exact planned files are:

1. `AGENTS.md`
2. `README.md`
3. `PRODUCT.md`
4. `MVP.md`
5. `PROJECT_BOUNDARY.md`
6. `DATA_SCOPE.md`
7. `APPROVALS.md`
8. `PHASE_PLAN.md`
9. `STATUS.md`
10. `ACCEPTANCE_TRACE.md`
11. `AGENTS.override.md`
12. `STATUS.profile.md`
13. `SAFETY_POLICY.profile.md`
14. `VERIFICATION.profile.md`

This list must remain equal to the renderer's `standard` base outputs followed
by its `standard` selected-profile outputs. The contract does not authorize a
render, target write, overwrite, or curated-example change.

## Safety And Data Boundary

Only synthetic CSV and JSON fixtures may be used in future implementation and
verification until a separate task explicitly approves other data. Actual
business, personal, customer, private, credential, secret, equipment, device,
or live data is forbidden.

The target alias is safe to persist. An owner-selected absolute path must not
be added to harness documents, fixtures, logs, or closeout evidence. Target
repository creation, `git init`, rendering, package installation, and
application implementation require separate approval.

All future validation must remain local and read-only with respect to its
inputs. `performed_actions=[]` records that the quality check itself performs
no external or mutating action.

## Non-goals

Version 1 does not include:

- CSV modification or cleanup;
- output-file or report persistence;
- recursive directory scanning or batch input;
- JSON, Excel, spreadsheet, database, or archive data input;
- network, API, remote storage, AI, or LLM use;
- visualization or dashboard generation;
- composite uniqueness or cross-file checks;
- an external dependency;
- target creation, `git init`, render, implementation, stage, commit, push,
  workflow dispatch, artifact upload, release, publication, or downstream
  access; or
- corpus digest or release-evidence regeneration.

## Verification

This contract is accepted locally only when all of these checks pass:

- the focused contract suite reports six passing tests;
- the full suite remains green;
- standalone eval reports all cases passing without changing its tracked
  report;
- all nine quality gates pass;
- all five release checksums match;
- the exact approved 34-source corpus remains valid with no stale source;
- only the two allowed files differ; and
- release evidence, corpus digest, and eval report remain byte-identical.

## Next Step

After this contract commit has a clean Local Verify run, plan a separate
`Greenfield Repository Initialization` task. Only that task may seek approval
for an exact target path, directory creation, `git init`, an operating-system
temporary `python_cli` plus `standard` render probe, installation of the exact
14 documents, and an initial commit decision.

CSV CLI implementation remains a later, separately approved step after the
initialized repository and rendered documents have been reviewed.
