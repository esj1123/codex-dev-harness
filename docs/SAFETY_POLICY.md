# SAFETY_POLICY.md

## Purpose

Define safety defaults for AI/Codex work using this template.

## Side Effects

Side effects include:
- File write, delete, move, rename, or permission change.
- Email send, reply, or forward.
- Database insert, update, delete, or migration apply.
- External API mutation.
- Live target write.
- PLC or equipment write, start, stop, reset, or mode change.

## Required Order

1. Read-only inspection.
2. Dry-run or expected change summary.
3. Review of expected changes.
4. Explicit confirmation for risky side effects.
5. Apply only within approved scope.
6. Closeout with evidence.

## Private Data Protection

Do not include:
- Secrets, credentials, keys, or tokens.
- Private raw input.
- Sensitive business source text.
- Device addresses, device parameters, or live-control values.

Use synthetic fixtures and summaries instead of private raw input.

## PLC and Equipment Work

Simulator or mock comes first. Live write, start, stop, reset, and mode change are high-risk side effects and are not part of P0.
