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

## Current Status

The historical P0 profile descriptions have been extended with concrete profile template folders and example skeletons. Additional profiles should not be added casually; new profiles need a clear validation example and safety policy.
