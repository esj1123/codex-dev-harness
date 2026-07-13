# Phase 11D.2 Temporary Synthetic Filled-Contract Usage Probe

## Purpose

Record the Phase 11D.2 review-only usage probe for the standalone downstream
task-contract validator in `filled` mode.

The probe uses one deterministic synthetic contract created only under the
operating-system temporary root. It does not create a tracked filled contract,
select or access a downstream repository, authenticate approval evidence,
execute a declared command, or perform a write, network, remote, release,
deployment, or live action.

## Probe Basis

| item | observed value |
|---|---|
| validator implementation commit | `74c299063effec2746a913a66172bb4fd2a7bbde` |
| Phase 11D.1 checkpoint commit | `8e785911234823ed1b756df839bba6daa86502db` |
| prerequisite Local Verify run | `29214127666` |
| prerequisite Local Verify job | `86706793341` |
| prerequisite tests | `521 passed` |
| prerequisite quality gate | `9/9 PASS` |
| prerequisite artifact uploads | `0` |
| input class | temporary synthetic filled contract |
| contract kind | `filled` |
| validator mode | read-only `--dry-run --json` |

The prerequisite Local Verify checked out the Phase 11D.1 checkpoint exactly,
used read-only contents permission, passed all three profile render dry-runs,
and uploaded no artifact.

## Temporary Candidate

The candidate was copied in memory from the tracked Phase 11B synthetic fixture
and written as UTF-8 deterministic pretty JSON with sorted keys, LF line endings,
and a final newline. The candidate was 5,440 bytes and remained below the 64 KiB
input boundary.

Selected synthetic fields were:

| field group | selected value |
|---|---|
| fixture id | `phase-11d2-synthetic-filled-contract` |
| synthetic marker | `false`, required to exercise filled-mode validation |
| repository access class | `local_read_only` |
| repository state | generalized alias, synthetic commits, synthetic branch/ref, `clean` |
| allowed scope | `docs/README.md`, read-only |
| no-touch scope | `restricted/config.json` |
| declared command | `git status --short`, status `NOT RUN` |
| declared effects | `repository_access`, `execute` |
| authorized permission records | `repository_access`, `execute` |
| unauthorized permission records | remaining 14 side-effect classes |
| persistence | none |
| performed actions | `[]` |

The approval flags and approval references were bounded synthetic fixture data
needed to test internal field consistency. They were not owner approval,
target-repository approval, authenticated evidence, or permission to perform an
action.

The candidate was built with the Python standard library without importing the
test-local fixture helper. No helper, candidate, validator output, receipt,
trace, audit log, or artifact was written inside the repository.

## Probe Command

```text
python scripts/downstream_task_contract_validator.py --contract <OS_TEMP_JSON> --contract-kind filled --dry-run --json
```

`<OS_TEMP_JSON>` represents the ephemeral control path. The actual absolute
path and raw JSON payload are intentionally not recorded.

## Observed Result

| field | observed value |
|---|---|
| validator exit code | `0` |
| status | `PASS` |
| reason codes | `[]` |
| validation issue count | `0` |
| authorized permission count | `2` |
| unauthorized permission count | `14` |
| authorized classes | `repository_access`, `execute` |
| downstream repository access | `NOT RUN` |
| network read | `NOT RUN` |
| command execution | `NOT RUN` |
| downstream write | `NOT RUN` |
| performed actions | `[]` |
| temporary cleanup | `PASS` |

The temporary JSON and its unique `phase-11d2-` directory were deleted
immediately after validation. A post-probe check found no matching temporary
directory, tracked change, or untracked repository file.

## Interpretation

`PASS` means only that the selected synthetic filled contract satisfied the
validator's internal structure, safety, approval-field, permission-ceiling, and
command-effect consistency checks.

It does not mean that approval evidence was authenticated, a target repository
was inspected, `git status --short` was executed, or downstream access was
authorized. The declared command remained inert JSON data and every external
state remained `NOT RUN`.

## Safety Confirmation

The probe did not use a real downstream repository identifier, path, branch,
remote, source, private value, live configuration, IP, endpoint, credential,
token, raw source, diff, patch, stdout transcript, stderr transcript, command
log, approval text, tool-call body, or downstream evidence.

Phase 11D.2 does not modify the validator, tests, Phase 11B fixture, `STATUS.md`,
the capability roadmap, `ACCEPTANCE_TRACE.md`, schemas, gates, workflows,
artifacts, audits, evals, templates, profiles, examples, release evidence, or
the exact 34-source corpus digest.

## Decision

Phase 11D.2 is accepted as `PASS` with decision `no runtime patch required`.
The filled-mode result remains synthetic, local-only, read-only, non-persistent,
and non-authorizing.

## Next Step

The next separately controlled task is Phase 11A-D.2 current handoff
synchronization followed by an exact same-34-source corpus digest freshness
repair. The handoff must keep release evidence regeneration on `HOLD` and must
not select or access a real downstream repository.

A real downstream task remains blocked until the owner separately names the
target authority, safe repository alias, access class, exact commands, allowed
files, no-touch paths, verification, cleanup, and every permitted side effect.
