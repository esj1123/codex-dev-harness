# DATA_SCOPE.md

## Purpose

Define data scope for `plc_tool_minimal`.

## Data Classes

| data class | allowed | storage | notes |
|---|---|---|---|
| synthetic simulator fixture | yes | repository allowed | Documentation-only placeholder |
| generated docs | yes | example folder | Current skeleton output |
| private input | no | repository prohibited | Not used in this example |
| secrets | no | repository prohibited | Not used in this example |
| live configuration | no | repository prohibited | Not used in this example |

## Verification Notes

- simulator/mock first.
- live device write prohibited.
- live behavior: NOT RUN.
- start/stop/reset/mode change: NOT RUN and prohibited in this skeleton.

