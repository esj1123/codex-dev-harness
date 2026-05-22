# PROFILE_MATRIX.md

## Purpose

Define operating profiles for applying this template to different project risk levels.

## Conceptual Profiles

| profile | purpose | orchestration | side-effect default | verification default | suitable projects |
|---|---|---|---|---|---|
| inspection | Review structure and risks | one-agent read-only | disallowed | file review and findings | initial repo assessment |
| governed_coding | Make small safe changes | one-agent inspect-plan-change-verify | dry-run first | unit, smoke, acceptance trace | Python/C# tools, small apps |
| workflow_orchestration | Manage staged workflows | one-agent with limited helper use | approval required for mutation | stage gate and runtime trace | pipelines and operational workflows |
| multi_agent_lab | Experiment with role split | sandboxed role separation | no live target mutation | cross-review and merge risk notes | agent workflow research |
| managed_enterprise | Operate under organization policy | audited tools only | approval-gated | policy validation and audit evidence | regulated or sensitive environments |

## Implemented Template Profiles

| implemented profile | status | example | notes |
|---|---|---|---|
| python_cli | available | examples/python_cli_minimal | pytest and CLI smoke are expected but NOT RUN in skeleton |
| csharp_desktop | available | examples/csharp_desktop_minimal | build/test/smoke are expected but NOT RUN in skeleton |
| plc_or_device_tool | available | examples/plc_tool_minimal | simulator/mock first and live device write prohibited |

Implemented profiles are regression and example variants for validating the template system. They are not a promise to create a dedicated profile for every downstream project type.

## Base Template Coverage

The base template now carries reusable planning and governance surfaces that should apply across many project types:

- `SOURCE_INDEX.md` for source inventory and allowed use.
- `PROJECT_BOUNDARY.md` for scope, no-touch zones, and approval-required changes.
- `DATA_SCOPE.md` for private input, synthetic fixtures, generated output, and forbidden material.
- `PHASE_PLAN.md` for phase-gated execution.
- `APPROVALS.md` for recording explicit approvals before side effects.

These base documents are the preferred way to support complex downstream projects before adding a new profile.

## Downstream Candidates

| candidate | treatment | rationale |
|---|---|---|
| scenario simulator design | downstream application candidate, not a built-in profile | It needs source indexing, boundary control, phase planning, and approval records, but does not yet prove a reusable profile category |
| local automation tool | downstream application candidate | Use base template plus existing profiles when a runtime match exists |
| documentation-only planning repo | downstream application candidate | Use base template without runtime-specific profile expansion |

## Current Status

The historical P0 profile descriptions have been extended with concrete profile template folders and example skeletons. Additional profiles should not be added casually; profile creation is an approval-gated side effect and needs repeated reuse evidence, a validation example, and a safety policy.
