# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| `main` | Yes |
| `v0.1.0` | Yes |
| `v0.1.0-rc1` | No |
| `v0.1.0-rc2` | No |

## Scope

This policy covers vulnerabilities in the `codex-dev-harness` repository,
including its scripts, quality gates, template rendering behavior, committed
workflow definitions, and repository-owned evidence tooling.

Projects rendered from or adapted from this harness are downstream projects.
They are outside this repository's support scope and must define their own
security policy and reporting channel. A downstream issue is in scope here only
when it is reproducible as a defect in the harness itself.

## Reporting A Vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's
[Report a vulnerability](https://github.com/esj1123/codex-dev-harness/security/advisories/new)
channel so the report remains private while it is assessed.

Include only the information needed to validate the issue:

- a concise summary and expected impact;
- the affected branch, tag, commit, or component;
- minimized reproduction steps using synthetic data; and
- any known mitigation or workaround.

Do not submit secrets, credentials, private data, live configuration, device
values, raw command logs, or unrelated downstream data. Redact sensitive values
and replace them with bounded synthetic fixtures.

## Response Targets

The maintainer aims to acknowledge a private report within 7 calendar days and
provide a status update at least every 14 calendar days while investigation or
remediation remains active. Remediation timing depends on severity,
reproducibility, and verification needs.

This policy does not guarantee a fix deadline, bounty, CVE assignment, or
publication schedule.

## Coordinated Disclosure

Allow the maintainer reasonable time to validate and address the report before
public disclosure. Any advisory publication or coordinated disclosure date
must be agreed through the private report.
