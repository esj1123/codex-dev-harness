# Safety Pattern Checks

## 결론

이 문서는 downstream docs-only readiness output을 stage하기 전에 수행할 reusable safety pattern check 방식을 정의한다.

Pattern check는 secrets, private data, live configuration이 없다는 증명이 아니다. 목적은 새로 생성되거나 수정된 허용 문서에서 위험 신호를 보수적으로 찾고, matched value를 출력하지 않은 채 path와 finding category만 보고하는 것이다.

## 사용 목적

- Generated downstream docs에 private value가 섞였는지 stage 전에 보수적으로 확인한다.
- Policy wording과 possible private value를 구분한다.
- Closeout에서 matched value를 복사하지 않고 path-only evidence를 남긴다.
- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`의 safety pattern check 항목을 일관되게 수행한다.

이 문서는 downstream repository에 대한 write approval, implementation approval, push approval, PR approval을 제공하지 않는다.

## 적용 대상

적용 대상:

- `<CHANGED_DOCS>`
- `<ALLOWED_DOCS>`
- downstream docs-only readiness baseline 문서
- stage 전 review 대상 문서

적용 대상이 아닌 항목:

- source code deep review
- binary files
- generated artifacts
- live target configuration
- mail bodies
- vault contents
- broker data
- customer data
- device, PLC, RSID, Outlook, broker, vault, or production system access

## 기본 원칙

- Pattern checks are not proof that secrets or private data are absent.
- Policy wording matches are not automatic failures.
- Real-looking private values require stop and report.
- Do not paste matched private values into closeout.
- Report only file path, finding category, and whether it appears to be policy wording or possible private value.
- Use path-only output by default, such as `rg -l`.
- Do not use value-printing output such as `rg -n` unless the task explicitly approves manual review.
- Scope checks to newly created or modified allowed docs only.

## path-only safety check rule

Default report shape:

```text
<FILE_PATH>: <FINDING_CATEGORY>: <policy_wording_only | possible_private_value>
```

Allowed report fields:

- file path
- finding category
- interpretation: `policy_wording_only` or `possible_private_value`
- whether review stopped

Forbidden report fields:

- matched secret value
- token value
- account number
- email body
- IP value
- port value
- equipment value
- live configuration value
- customer data
- vault content

If a match looks like a real private value, stop. Do not paste the value into the response. Report only the file path and category.

## policy wording vs possible private value

Policy wording examples:

- A safety policy says credentials must not be committed.
- A handoff note says live configuration must not be printed.
- A checklist says customer data must not be copied.
- A verification doc says vault or mail contents are out of scope.

These matches are usually `policy_wording_only` when they describe forbidden behavior rather than containing actual values.

Possible private value indicators:

- A string appears to be a real credential, token, or secret.
- A line appears to contain a real network address or port assignment.
- A line appears to contain a real equipment parameter or live configuration.
- A line appears to contain customer-identifying data.
- A line appears copied from mail, vault, broker, or internal private source content.

When unsure, classify as `possible_private_value` and stop for user review.

## recommended patterns

Use these categories in closeout and review notes:

| Category | Intended use |
| --- | --- |
| `credential_like` | Words or shapes associated with credentials, secrets, keys, passwords, auth, or login data. |
| `token_like` | Words or shapes associated with API tokens, bearer tokens, session tokens, or access tokens. |
| `ip_like` | Network address-like text. Report path only. |
| `port_like` | Port assignment or endpoint wording. Report path only. |
| `private_live_wording` | Policy or content mentioning private, live, production, runtime, or configuration boundaries. |
| `customer_data_wording` | Policy or content mentioning customer, account, personal, or private user data. |
| `equipment_value_wording` | Policy or content mentioning device, PLC, equipment, sensor, actuator, RSID, or control values. |
| `vault_or_mail_wording` | Policy or content mentioning vault, notes, mail, mailbox, attachments, or message bodies. |
| `policy_wording_only` | Interpretation category for matches that are only safety-policy wording. |
| `possible_private_value` | Interpretation category for matches that may contain a real private value. |

Pattern lists should remain conservative. A finding is a review signal, not automatic proof of a problem.

## forbidden reporting behavior

Do not report:

- matched line contents
- surrounding context lines
- highlighted snippets
- decoded or normalized matched values
- copied source excerpts
- actual account, endpoint, credential, token, equipment, mail, vault, broker, customer, or live config data

Do not write:

```text
Found token: <MATCHED_VALUE>
Found endpoint: <MATCHED_VALUE>
Found customer value: <MATCHED_VALUE>
```

Write:

```text
<FILE_PATH>: token_like: possible_private_value
<FILE_PATH>: private_live_wording: policy_wording_only
```

## rg command examples

Run from `<REPO_ROOT>` and scope to `<CHANGED_DOCS>` or `<ALLOWED_DOCS>`.

Credential-like wording:

```powershell
rg -l --pcre2 "(?i)(credential|secret|password|passwd|api[_ -]?key|auth|login)" <CHANGED_DOCS>
```

Token-like wording:

```powershell
rg -l --pcre2 "(?i)(token|bearer|session|access[_ -]?token)" <CHANGED_DOCS>
```

Network address-like text:

```powershell
rg -l --pcre2 "\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b" <CHANGED_DOCS>
```

Port-like wording:

```powershell
rg -l --pcre2 "(?i)\b(port|endpoint|host|url|uri)\b" <CHANGED_DOCS>
```

Private or live wording:

```powershell
rg -l --pcre2 "(?i)(private|live|production|runtime|config|configuration)" <CHANGED_DOCS>
```

Customer-data wording:

```powershell
rg -l --pcre2 "(?i)(customer|account|personal|PII|private user)" <CHANGED_DOCS>
```

Equipment or control wording:

```powershell
rg -l --pcre2 "(?i)(equipment|device|PLC|RSID|sensor|actuator|control value)" <CHANGED_DOCS>
```

Vault or mail wording:

```powershell
rg -l --pcre2 "(?i)(vault|mail|mailbox|email|attachment|message body)" <CHANGED_DOCS>
```

Use `rg -l` by default because it prints file paths only. Avoid `rg -n`, `rg -C`, or unrestricted `rg` output in closeout unless the task explicitly approves manual value review.

## PowerShell Select-String fallback

If `rg` is not available, use PowerShell in a way that returns paths only.

Credential-like fallback:

```powershell
Select-String -Path <CHANGED_DOCS> -Pattern "(?i)(credential|secret|password|passwd|api[_ -]?key|auth|login)" |
  Select-Object -ExpandProperty Path -Unique
```

Token-like fallback:

```powershell
Select-String -Path <CHANGED_DOCS> -Pattern "(?i)(token|bearer|session|access[_ -]?token)" |
  Select-Object -ExpandProperty Path -Unique
```

Private or live wording fallback:

```powershell
Select-String -Path <CHANGED_DOCS> -Pattern "(?i)(private|live|production|runtime|config|configuration)" |
  Select-Object -ExpandProperty Path -Unique
```

Do not include the default `Select-String` match output in final reports, because it may print matched values. Pipe to `Select-Object -ExpandProperty Path -Unique` or manually redact output before reporting.

## closeout reporting format

Use this closeout block for downstream docs-only readiness review:

```text
Safety pattern check:
- Scope: <CHANGED_DOCS> within <ALLOWED_DOCS>
- Output mode: path-only
- Private values printed: no
- Findings:
  - <FILE_PATH>: <FINDING_CATEGORY>: <policy_wording_only | possible_private_value>
- Stopped for user review: <yes | no>
- Note: Pattern checks are not proof that secrets or private data are absent.
```

If there are no path-only findings:

```text
Safety pattern check:
- Scope: <CHANGED_DOCS> within <ALLOWED_DOCS>
- Output mode: path-only
- Findings: none
- Private values printed: no
- Note: Pattern checks are not proof that secrets or private data are absent.
```

## integration with downstream readiness review checklist

Use this guide with `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`.

Checklist integration points:

- Confirm checks were scoped to modified allowed docs only.
- Confirm path-only output was used.
- Confirm findings were interpreted as `policy_wording_only` or `possible_private_value`.
- Confirm possible private values caused a stop.
- Confirm matched values were not pasted into closeout.
- Confirm policy wording matches were not treated as automatic failures.

If safety interpretation is missing, the review result should be `needs_tuning`. If a possible private value is present, the review result should be `blocked`.

## risks / limitations

- Pattern checks can miss private values.
- Pattern checks can produce false positives from policy wording.
- Path-only output does not explain why a match happened.
- Manual review may be needed, but it must not paste private values into the final report.
- A clean pattern check is not permission to write code, run builds, push, open PRs, call external services, or touch live targets.
- This guide does not modify scanner logic, templates, prompt templates, quality gates, CI, RAG, retrieval, embeddings, model calls, external services, or downstream repositories.
