# Python Runtime Policy

## Purpose

Define the local Python runtime and development dependency policy for
codex-dev-harness verification.

This policy improves local verification reproducibility. It does not add
runtime application dependencies, a package manager, CI workflow, cloud
deployment behavior, application code, device code, or live target behavior.

## Pinned Runtime

The repository pins the local verification runtime in `.python-version`:

- Python `3.12.10`

This pin matches the hosted Windows verification runtime and the final Python
3.12 release with Windows binary installers. Contributors may use another
compatible Python 3.12 runtime for focused local work, but exact
`LOCAL_INTEGRATION (V2)` and `HOSTED_EXACT_SHA (V3)` verification require the
pinned patch version. Tier meaning is defined only in
`docs/VERIFICATION.md`.

## Development Dependencies

Development dependencies are split into two files:

- `requirements-dev.txt`: minimal direct development dependencies used by the
  focused development and narrow test commands.
- `requirements-dev.lock`: exact local verification dependency set for the
  pinned Python runtime and the Local Verify/release wrappers.

`requirements-dev.txt` should stay small and contain only direct development
requirements needed by this repository. It is not a place for application,
device, C#, PLC, cloud deployment, or live-target dependencies.

`requirements-dev.lock` is a pip-compatible exact pin and SHA-256 hash set for
reproducing the Windows x64 local verification dependency environment. It
includes `pytest` and the pytest dependency packages observed in the local
verification runtime. Exact verification permits only those locked packages
plus the bootstrap `pip` distribution supplied by the isolated environment.
Any other installed distribution, including an unrelated package bundled with
another Python runtime, fails the environment gate.

## Recommended Commands

For focused development or a narrow test:

```powershell
python --version
python -m pip install -r requirements-dev.txt
```

For `scripts/run_local_verify.ps1`, `scripts/run_release_verify.ps1`, or another
exact `LOCAL_INTEGRATION (V2)` verification run:

```powershell
python --version
python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
python scripts/verify_dev_environment.py --expected-version-file .python-version --lock requirements-dev.lock --json
python -m pip check
```

On Windows, create an ignored repository-local environment with the pinned
runtime when practical:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
```

An explicit `PYTHON` environment variable has first selection priority. The
verification wrappers then consider `.venv\Scripts\python.exe`, system
`python`, the Python 3.12 launcher, and the Codex bundled fallback in that
order. Every selected interpreter must expose exactly the locked distributions
plus bootstrap `pip`; selection priority is not an environment-check bypass.

Focused work may then run its scoped pytest command. The Local Verify wrapper
uses the exact environment and runs, in order:

```powershell
python -m pytest tests --durations=50 -rs
python scripts/run_eval.py
python scripts/quality_gate.py
```

The wrapper then performs the three profile render dry-runs documented in
`docs/VERIFICATION.md`.

If `scripts/run_release_verify.ps1` is present and the task explicitly allows
local release evidence regeneration, run it as a final local wrapper check.

## Lock Update Rule

Changing `.python-version`, `requirements-dev.txt`, or
`requirements-dev.lock` is a reproducibility-impacting change. Update them only
when the task explicitly approves runtime or dependency changes.

When updating the lock:

- keep Python aligned with `.python-version`
- exact-pin every package and include at least one approved SHA-256 wheel hash
- validate hashes against official package release metadata
- install with `--require-hashes --only-binary=:all:`
- pin exact versions with `==`
- include only development verification dependencies
- exclude unrelated bundled packages
- do not add a new package manager without separate approval
- do not add application, device, cloud, C#, PLC, or live-target dependencies

## Known Limitations

The lock permits only the recorded universal wheels for the approved Windows
x64/Python 3.12.10 verification environment. A platform-specific dependency,
new hash, source distribution, or package/version change requires a separate
owner-approved dependency locking task.

The release manifest inventory includes `.python-version`,
`requirements-dev.txt`, and `requirements-dev.lock` when those files are
present. The manifest records them as file inventory evidence only; dependency
changes remain governed by the lock update rule above.

Bare `python.exe` may be unavailable in some Codex desktop Windows shells. In
that case, verification may use the repository-local environment or another
runtime selected by `scripts/run_local_verify.ps1` and should report the bare
Python command as ENVIRONMENT BLOCKED.
