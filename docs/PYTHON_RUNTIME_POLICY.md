# Python Runtime Policy

## Purpose

Define the local Python runtime and development dependency policy for
codex-dev-harness verification.

This policy improves local verification reproducibility. It does not add
runtime application dependencies, a package manager, CI workflow, cloud
deployment behavior, application code, device code, or live target behavior.

## Pinned Runtime

The repository pins the local verification runtime in `.python-version`:

- Python `3.12.13`

This pin matches the currently used local verification runtime in the Codex
desktop environment. Contributors may use another compatible Python 3.12
runtime for local work, but release evidence and reproducibility reviews should
prefer the pinned version when practical.

## Development Dependencies

Development dependencies are split into two files:

- `requirements-dev.txt`: minimal direct development dependencies used by the
  standard local verification command.
- `requirements-dev.lock`: exact local verification dependency set for the
  pinned Python runtime.

`requirements-dev.txt` should stay small and contain only direct development
requirements needed by this repository. It is not a place for application,
device, C#, PLC, cloud deployment, or live-target dependencies.

`requirements-dev.lock` is a pip-compatible exact pin set for reproducing the
current local verification dependency environment. It includes `pytest` and the
pytest dependency packages observed in the local verification runtime. It
intentionally excludes unrelated packages bundled with the Codex desktop
runtime.

## Recommended Commands

For normal local verification setup:

```powershell
python --version
python -m pip install -r requirements-dev.txt
```

For exact local dependency reproduction:

```powershell
python --version
python -m pip install -r requirements-dev.lock
```

Then run:

```powershell
python -m pytest
python scripts/quality_gate.py
powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1
```

If `scripts/run_release_verify.ps1` is present and the task explicitly allows
local release evidence regeneration, run it as a final local wrapper check.

## Lock Update Rule

Changing `.python-version`, `requirements-dev.txt`, or
`requirements-dev.lock` is a reproducibility-impacting change. Update them only
when the task explicitly approves runtime or dependency changes.

When updating the lock:

- keep Python aligned with `.python-version`
- use standard pip-compatible requirement lines
- pin exact versions with `==`
- include only development verification dependencies
- exclude unrelated bundled packages
- do not add a new package manager without separate approval
- do not add application, device, cloud, C#, PLC, or live-target dependencies

## Known Limitations

The lock file does not include wheel hashes. It records exact package versions
only. Hash-locked, platform-specific wheel evidence would require a separate
owner-approved dependency locking task.

The current release manifest generator was not changed by this policy update.
If release manifests must inventory `.python-version` and
`requirements-dev.lock`, update `scripts/generate_manifest.py` in a separate
approved generator-alignment task.

Bare `python.exe` may be unavailable in some Codex desktop Windows shells. In
that case, verification may use the local runtime selected by
`scripts/run_local_verify.ps1` and should report the bare Python command as
ENVIRONMENT BLOCKED.
