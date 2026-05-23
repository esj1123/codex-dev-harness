# DATA_SCOPE.md

## Purpose

Define data scope for `python_cli_minimal`.

## Data Classes

| data class | allowed | storage | notes |
|---|---|---|---|
| synthetic fixture | yes | repository allowed | Preferred for future tests |
| generated docs | yes | example folder | Current skeleton output |
| private input | no | repository prohibited | Not used in this example |
| secrets | no | repository prohibited | Not used in this example |
| live configuration | no | repository prohibited | Not used in this example |

## Verification Notes

- pytest: NOT RUN as runtime behavior.
- CLI smoke: NOT RUN as runtime behavior.
- Synthetic fixtures only.

