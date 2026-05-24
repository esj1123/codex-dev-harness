# Local Package Checklist

## Purpose

Define a local package boundary for using codex-dev-harness after `v0.1.0`.

This checklist is documentation-only. It does not build a package or write a release archive.

Machine-readable release bundle and manifest policy is documented in
`docs/RELEASE_BUNDLE_POLICY.md` and `docs/RELEASE_MANIFEST_POLICY.md`. Those
policies do not implement generators or create release artifacts.

## Included Files

Include:

- Root contract docs: `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `ROADMAP.md`, `STATUS.md`, `ACCEPTANCE_TRACE.md`, `code_review.md`.
- `docs/`.
- `templates/`.
- `profiles/`.
- `scripts/`.
- `examples/`.
- `tests/`.
- `requirements-dev.txt`.
- `template.config.example.yml`.

Future machine-readable release evidence may be included only after separate
approval and should follow `docs/RELEASE_BUNDLE_POLICY.md`.

## Excluded Files

Exclude:

- `.git/`.
- `.venv/`.
- `__pycache__/`.
- `.pytest_cache/`.
- Private input.
- Live configuration.
- Secrets, keys, tokens, credentials, and account material.
- Raw source bundles.
- Downstream generated target output.
- Temporary local adoption targets.
- Clean clone validation working folders.
- Generated release manifests, checksums, SBOMs, provenance, audit sessions,
  eval reports, and release archives unless a separate release bundle task
  explicitly approves them.

## Local Verification Before Packaging

Run local verification before packaging:

- `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`
- local Python runtime `scripts/quality_gate.py`

Packaging should not proceed if docs, hygiene, template schema, examples, render drift, or secret scan gates fail.

## Safety Checklist

- No secrets.
- No raw source.
- No private input.
- No live values.
- No live configuration.
- No IP/port/tag/live parameter values.
- No real application code added for packaging.
- No PLC/device code.
- No live target write support.
- No GitHub Actions workflow required.

## Notes

The local package should preserve the local-first baseline. It should not become a distribution vehicle for downstream target output or sensitive source material.

Release bundle components such as `release-manifest.json`, `checksums.sha256`,
`sbom.spdx.json`, `sbom.cdx.json`, `provenance.intoto.jsonl`, and
`audit/session-*.jsonl` remain future optional artifacts. They are not generated
by this checklist.
