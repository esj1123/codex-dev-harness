[CmdletBinding()]
param(
    [ValidateSet("Full", "Routine")]
    [string]$Lane = "Full"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $RepoRoot

function Set-HermeticVerificationEnvironment {
    $ambientNames = @(
        "PYTEST_ADDOPTS",
        "PYTEST_PLUGINS",
        "PYTHONPATH",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_CONFIG",
        "GIT_CONFIG_PARAMETERS",
        "GIT_CONFIG_SYSTEM",
        "GIT_DIR",
        "GIT_EXEC_PATH",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_SHALLOW_FILE",
        "GIT_TEMPLATE_DIR",
        "GIT_WORK_TREE",
        "GIT_CONFIG_COUNT"
    )
    $dynamicConfigNames = @(
        [Environment]::GetEnvironmentVariables(
            [EnvironmentVariableTarget]::Process
        ).Keys | Where-Object {
            ([string]$_) -match '^GIT_CONFIG_(?:KEY|VALUE)_[0-9]+$'
        }
    )
    foreach ($name in @($ambientNames + $dynamicConfigNames)) {
        [Environment]::SetEnvironmentVariable(
            [string]$name,
            $null,
            [EnvironmentVariableTarget]::Process
        )
    }

    $disabledHooksPath = Join-Path (
        [System.IO.Path]::GetTempPath()
    ) ("codex-harness-disabled-hooks-{0}" -f [Guid]::NewGuid().ToString("N"))
    if (Test-Path -LiteralPath $disabledHooksPath) {
        throw "Unable to allocate a non-existent Git hooks path."
    }

    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    $env:GIT_CONFIG_NOSYSTEM = "1"
    $env:GIT_CONFIG_GLOBAL = "NUL"
    $env:GIT_TERMINAL_PROMPT = "0"
    $env:GCM_INTERACTIVE = "Never"
    $env:GIT_NO_REPLACE_OBJECTS = "1"
    $env:GIT_OPTIONAL_LOCKS = "0"

    $fixedGitConfig = @(
        @("commit.gpgSign", "false"),
        @("tag.gpgSign", "false"),
        @("core.hooksPath", $disabledHooksPath),
        @("core.fsmonitor", "false"),
        @("submodule.recurse", "false"),
        @("safe.directory", [System.IO.Path]::GetFullPath($RepoRoot))
    )
    $env:GIT_CONFIG_COUNT = [string]$fixedGitConfig.Count
    for ($index = 0; $index -lt $fixedGitConfig.Count; $index++) {
        [Environment]::SetEnvironmentVariable(
            "GIT_CONFIG_KEY_$index",
            [string]$fixedGitConfig[$index][0],
            [EnvironmentVariableTarget]::Process
        )
        [Environment]::SetEnvironmentVariable(
            "GIT_CONFIG_VALUE_$index",
            [string]$fixedGitConfig[$index][1],
            [EnvironmentVariableTarget]::Process
        )
    }
}

Set-HermeticVerificationEnvironment

function Find-Python {
    $candidates = @()
    if ($env:PYTHON) {
        $candidates += $env:PYTHON
    }

    $repoVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $repoVenvPython) {
        $candidates += $repoVenvPython
    }

    $candidates += "python"
    $candidates += "py"

    $codexPython = Join-Path $HOME ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $codexPython) {
        $candidates += $codexPython
    }

    foreach ($candidate in $candidates) {
        try {
            if ($candidate -eq "py") {
                & py -3.12 scripts/verify_dev_environment.py --expected-version-file .python-version --lock requirements-dev.lock --json *> $null
            } else {
                & $candidate scripts/verify_dev_environment.py --expected-version-file .python-version --lock requirements-dev.lock --json *> $null
            }
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        } catch {
            continue
        }
    }

    throw "No Python candidate satisfies .python-version and requirements-dev.lock. Install the exact development environment or set PYTHON."
}

$PythonCommand = Find-Python

function Invoke-PythonStep {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string[]]$PythonArgs
    )

    Write-Host "==> $Label"
    if ($PythonCommand -eq "py") {
        & py -3.12 @PythonArgs
    } else {
        & $PythonCommand @PythonArgs
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Error "$Label failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

$RoutineHeldTestFiles = @(
    "tests/test_agent_quality_aggregation.py",
    "tests/test_agent_quality_capture.py",
    "tests/test_agent_quality_cli.py",
    "tests/test_agent_quality_contracts.py",
    "tests/test_agent_quality_semantic_failure.py",
    "tests/test_agent_quality_trial_validation.py",
    "tests/test_agent_role_profiles.py",
    "tests/test_hermes_git_push_preflight.py",
    "tests/test_hermes_git_push_preflight_durable_writer_proposal.py",
    "tests/test_hermes_git_push_preflight_evidence_decision.py",
    "tests/test_hermes_git_push_preflight_output_contract.py",
    "tests/test_hermes_git_push_preflight_receipt_trace_plan.py",
    "tests/test_hermes_git_push_preflight_receipt_writer.py",
    "tests/test_hermes_git_push_preflight_schema_alignment.py",
    "tests/test_hermes_git_push_preflight_selection_review.py",
    "tests/test_hermes_git_push_preflight_tracked_receipt_contract.py",
    "tests/test_hermes_git_push_preflight_tracked_receipt_policy.py",
    "tests/test_hermes_git_push_preflight_tracked_receipt_post_generation_review.py",
    "tests/test_hermes_git_push_preflight_usage_probe.py",
    "tests/test_hermes_git_push_preflight_writer.py",
    "tests/test_hermes_git_push_preflight_writer_persistence_hold.py",
    "tests/test_hermes_mcp_security_alignment.py",
    "tests/test_hermes_preflight_caller_boundary.py",
    "tests/test_hermes_preflight_use_planning_contract.py",
    "tests/test_hermes_sidecar.py",
    "tests/test_hermes_sidecar_planning_contract.py",
    "tests/test_hermes_sidecar_result_schema_contract.py",
    "tests/test_local_rag_retriever.py",
    "tests/test_mcp_tool_boundary_contract.py"
)

$PytestArgs = @("-m", "pytest", "tests", "--durations=50", "-rs")
if ($Lane -eq "Routine") {
    foreach ($heldTestFile in $RoutineHeldTestFiles) {
        $heldTestPath = Join-Path $RepoRoot $heldTestFile
        if (-not (Test-Path -LiteralPath $heldTestPath -PathType Leaf)) {
            throw "Routine held test file is missing: $heldTestFile"
        }
        $PytestArgs += @("--ignore", $heldTestFile)
    }
}

Write-Host "Local verification lane: $Lane"
Invoke-PythonStep "development environment" @("scripts/verify_dev_environment.py", "--expected-version-file", ".python-version", "--lock", "requirements-dev.lock", "--json")
Invoke-PythonStep "pytest" $PytestArgs
Invoke-PythonStep "standalone eval" @("scripts/run_eval.py")
Invoke-PythonStep "quality gate" @("scripts/quality_gate.py")
Invoke-PythonStep "python_cli_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/python_cli_minimal/template.config.yml", "--target", "examples/python_cli_minimal", "--dry-run")
Invoke-PythonStep "csharp_desktop_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/csharp_desktop_minimal/template.config.yml", "--target", "examples/csharp_desktop_minimal", "--dry-run")
Invoke-PythonStep "plc_tool_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/plc_tool_minimal/template.config.yml", "--target", "examples/plc_tool_minimal", "--dry-run")

Write-Host "Local verification passed ($Lane)."
