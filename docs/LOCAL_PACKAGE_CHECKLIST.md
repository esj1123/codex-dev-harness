# Local Package Checklist

## Purpose

Define a local package boundary for using codex-dev-harness after `v0.1.0`.

This checklist is documentation-only. It does not build a package or write a release archive.

Machine-readable release bundle and manifest policy is documented in
`docs/RELEASE_BUNDLE_POLICY.md` and `docs/RELEASE_MANIFEST_POLICY.md`. Those
policies are implemented by the local release generators. The currently
tracked release bundle is `CURRENT / LOCAL_ONLY` for its recorded source basis.
That state does not authorize regeneration, packaging, tag, signing, upload,
publication, or remote release.

## Included Files

Include:

- Root contract docs: `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `ROADMAP.md`, `STATUS.md`, `ACCEPTANCE_TRACE.md`, `code_review.md`.
- `docs/`.
- `templates/`.
- `profiles/`.
- `scripts/`.
- `examples/`.
- `tests/`.
- `.python-version`, `requirements-dev.txt`, and `requirements-dev.lock`.
- `template.config.example.yml`.

Future machine-readable release evidence may be included only after a separate
artifact-regeneration and package-inclusion approval. It must follow
`docs/RELEASE_BUNDLE_POLICY.md` and bind the promoted exact source basis.

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

The wrapper runs full pytest, standalone eval, the eight core quality gates,
and three profile render dry-runs. Packaging should not proceed if any required
check fails.

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
- The installed manual GitHub workflow is not a packaging prerequisite and is
  not a required check.

## Notes

The local package should preserve the local-first baseline. It should not become a distribution vehicle for downstream target output or sensitive source material.

Release generators for `release-manifest.json`, `checksums.sha256`,
`sbom.spdx.json`, `sbom.cdx.json`, and `provenance.intoto.jsonl` are
implemented. This checklist does not itself run them, refresh tracked
artifacts, or approve future changes to eval-report inclusion. The current
tracked bundle is `VALID ANCESTOR / REFRESH REQUIRED` for the current HEAD and
remains internally valid for its recorded ancestor source basis. A manual
exact-SHA GitHub evidence export is contract-selected; this checklist does not
authorize its execution or package inclusion. Read `STATUS.md` for its current
implementation state.
