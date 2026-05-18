# PROFILE_MATRIX.md

## Purpose

Define operating profiles for applying this template to different project risk levels.

## Profiles

| profile | purpose | orchestration | side-effect default | verification default | suitable projects |
|---|---|---|---|---|---|
| inspection | Review structure and risks | one-agent read-only | disallowed | file review and findings | initial repo assessment |
| governed_coding | Make small safe changes | one-agent inspect-plan-change-verify | dry-run first | unit, smoke, acceptance trace | Python/C# tools, small apps |
| workflow_orchestration | Manage staged workflows | one-agent with limited helper use | approval required for mutation | stage gate and runtime trace | pipelines and operational workflows |
| multi_agent_lab | Experiment with role split | sandboxed role separation | no live target mutation | cross-review and merge risk notes | agent workflow research |
| managed_enterprise | Operate under organization policy | audited tools only | approval-gated | policy validation and audit evidence | regulated or sensitive environments |

## P0 Status

Profiles are described only. Profile folders and render behavior are future work.
