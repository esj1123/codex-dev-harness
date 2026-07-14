# Render Tier Usage Probe

## Purpose

Record the post-implementation usage probe for `minimal`, `standard`, and
`full` render-tier selection against an OS-temporary target.

The probe exercises the public renderer and readiness-scanner CLIs without
changing curated examples, repository artifacts, runtime behavior, tests,
workflows, or the approved corpus.

## Basis

| item | observed value |
|---|---|
| implementation commit | `2ee9f1f66aa204ef2d5de515b8bce0228c2c5028` |
| prerequisite Local Verify run | `29304225740` |
| prerequisite Local Verify job | `86994191170` |
| prerequisite tests | `577 passed` |
| prerequisite quality gate | `9/9 PASS` |
| prerequisite artifact uploads | `0` |
| selected profile | `python_cli` |
| tier source | explicit CLI override of a config with no `render.tier` |
| target class | unique OS-temporary directory |

The prerequisite workflow checked out the implementation commit exactly, used
read-only contents permission, passed all three existing profile dry-runs, and
uploaded no artifacts.

## Probe Procedure

Each tier used the existing example config as read-only input and a distinct
temporary target. The command forms were:

```text
python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target <OS_TEMP_TARGET> --tier <TIER> --dry-run
python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target <OS_TEMP_TARGET> --tier <TIER>
python scripts/ai_readiness_scanner.py --json <OS_TEMP_TARGET>
```

The dry-run was required to leave its target absent. The actual render then
wrote Markdown only under the temporary target. The probe compared the exact
file set with the tier contract and checked contiguous Read Order closure in
`AGENTS.md`, `README.md`, and `AGENTS.override.md` before scanning readiness.
No `--force` option was used.

## Observed Results

| tier | dry-run plan | dry-run target created | rendered files | exact file set | Read Order closure | scanner score | scanner result |
|---|---:|---|---:|---|---|---:|---|
| `minimal` | 8 | no | 8 | PASS | PASS | 9 | `LIMITED_AI_ASSISTED_WORK_ALLOWED` |
| `standard` | 14 | no | 14 | PASS | PASS | 13 | `READY_FOR_AI_ASSISTED_WORK` |
| `full` | 16 | no | 16 | PASS | PASS | 13 | `READY_FOR_AI_ASSISTED_WORK` |

All three rendered file sets matched the contract exactly. Every orientation
document used contiguous numbering, referenced only emitted files, and
contained no unresolved `render.read_order` marker.

The `minimal` result is the contract's intended lower-cost readiness level.
Its missing acceptance-trace and status dimensions are consequences of the
explicit 8-file tier, not evidence of a renderer defect. The `standard` and
`full` results met the required ready threshold.

## Safety And Cleanup

- The repository remained clean throughout temporary rendering and cleanup.
- The temporary targets and their parent probe directory were deleted after
  result selection; cleanup was confirmed successful.
- The corpus digest, five release-evidence files, and eval report retained
  their pre-probe Git blob hashes.
- No curated example, template, renderer, test, config, schema, gate, workflow,
  artifact, receipt, trace, audit log, or downstream repository was modified.
- No network access, dependency installation, hook, post-action, overwrite,
  release, upload, publication, or live action was performed.
- This record excludes the temporary absolute path, raw JSON, raw stdout,
  shell transcript, token, credential, private value, and local environment
  detail.

## Decision

The probe is accepted as `PASS` with decision `no runtime patch required`.
Config omission remained full-compatible, explicit CLI tier selection produced
the expected plans and outputs, Read Order closure held, and all readiness
thresholds were met.

## Next Step

The next separate task is Render Tier handoff synchronization. It should update
only the current handoff surfaces that are demonstrably stale, then refresh the
existing exact 34-source corpus digest only if an included source changed.
Curated example regeneration, downstream application, and any workflow or
release expansion remain separate owner-approved decisions.
