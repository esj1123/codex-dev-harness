[CmdletBinding()]
param(
    [ValidateSet("Full", "Routine", "Core")]
    [string]$Lane = "Full",
    [AllowNull()]
    [string]$PytestBaseTempRoot,
    [switch]$EnvironmentOnly,
    [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ExpectedCommandIds = @(
    "development_environment",
    ("{0}_pytest" -f $Lane.ToLowerInvariant()),
    "standalone_eval",
    "quality_gate",
    "render_python_cli_minimal",
    "render_csharp_desktop_minimal",
    "render_plc_tool_minimal"
)
$stepRecords = foreach ($commandId in $ExpectedCommandIds) {
    [ordered]@{
        command_id = $commandId
        status = "NOT RUN"
        exit_code = $null
        safe_argv = $null
        invocation_sha256 = $null
        reason_codes = @()
    }
}
$RunResult = [ordered]@{
    schema_version = "1"
    checker_id = "local_verify_run"
    lane = $Lane
    status = "FAIL"
    exit_code = 1
    wrapper_sha256 = $null
    source_binding_scope = "wrapper_only"
    reason_codes = @()
    steps = @($stepRecords)
}
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Add-RunReasonCode {
    param([Parameter(Mandatory = $true)][string]$ReasonCode)

    $RunResult.reason_codes = @(
        @($RunResult.reason_codes + $ReasonCode) | Sort-Object -Unique
    )
}

function Get-RunAssessment {
    $reasonCodes = New-Object System.Collections.Generic.List[string]
    $steps = @($RunResult.steps)
    if ($steps.Count -ne $ExpectedCommandIds.Count) {
        $reasonCodes.Add("STEP_RECORD_COUNT_INVALID")
    } else {
        for ($index = 0; $index -lt $ExpectedCommandIds.Count; $index++) {
            $step = $steps[$index]
            if ($step.command_id -cne $ExpectedCommandIds[$index]) {
                $reasonCodes.Add("STEP_RECORD_ORDER_INVALID")
            }
            if ($step.status -cne "PASS") {
                $reasonCodes.Add("REQUIRED_STEP_NOT_PASS")
            }
            if ($null -eq $step.exit_code -or [int]$step.exit_code -ne 0) {
                $reasonCodes.Add("REQUIRED_STEP_EXIT_NOT_SUCCESS")
            }
            if (
                $null -eq $step.safe_argv -or
                $null -eq $step.invocation_sha256
            ) {
                $reasonCodes.Add("REQUIRED_STEP_EVIDENCE_MISSING")
            }
        }
    }
    return @($reasonCodes | Sort-Object -Unique)
}

function Complete-ExecutionResult {
    param([Parameter(Mandatory = $true)][int]$ExitCode)

    $existingReasons = @($RunResult.reason_codes)
    $assessmentReasons = @(Get-RunAssessment)
    $RunResult.reason_codes = @(
        @($existingReasons + $assessmentReasons) | Sort-Object -Unique
    )
    $effectiveExitCode = $ExitCode
    if (
        $ExitCode -eq 0 -and
        ($existingReasons.Count -ne 0 -or $assessmentReasons.Count -ne 0)
    ) {
        $effectiveExitCode = 1
    }
    $RunResult.exit_code = $effectiveExitCode
    if (
        $existingReasons.Count -eq 0 -and
        $assessmentReasons.Count -eq 0 -and
        $effectiveExitCode -eq 0
    ) {
        $RunResult.status = "PASS"
    } else {
        $RunResult.status = "FAIL"
    }
    [Console]::Out.WriteLine(
        ($RunResult | ConvertTo-Json -Compress -Depth 6)
    )
    exit $effectiveExitCode
}

function Stop-SetupFailure {
    param(
        [Parameter(Mandatory = $true)][string]$ReasonCode,
        [Parameter(Mandatory = $true)][string]$TextMessage
    )

    if ($Json -and -not $EnvironmentOnly) {
        Add-RunReasonCode -ReasonCode $ReasonCode
        Complete-ExecutionResult -ExitCode 1
    }
    throw $TextMessage
}

function Get-Sha256Hex {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LiteralPath
    )

    $stream = $null
    $sha256 = $null
    try {
        $stream = [System.IO.File]::OpenRead($LiteralPath)
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $hashBytes = $sha256.ComputeHash($stream)
        return (
            [System.BitConverter]::ToString($hashBytes) -replace "-", ""
        ).ToLowerInvariant()
    } finally {
        if ($null -ne $sha256) {
            $sha256.Dispose()
        }
        if ($null -ne $stream) {
            $stream.Dispose()
        }
    }
}

function Get-InvocationSha256Hex {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Tokens
    )

    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $joined = [string]::Join([char]0, $Tokens)
        $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($joined)
        $hashBytes = $sha256.ComputeHash($bytes)
        return (
            [System.BitConverter]::ToString($hashBytes) -replace "-", ""
        ).ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
}

function New-PytestBaseTempPath {
    param(
        [AllowNull()]
        [string]$Root
    )

    if ($null -eq $Root) {
        return $null
    }
    if ([string]::IsNullOrWhiteSpace($Root)) {
        throw "PytestBaseTempRoot must not be empty or whitespace."
    }
    if (-not [System.IO.Path]::IsPathRooted($Root)) {
        throw "PytestBaseTempRoot must be an absolute path outside the repository."
    }

    $resolvedRoot = [System.IO.Path]::GetFullPath($Root)
    $resolvedRepo = [System.IO.Path]::GetFullPath($RepoRoot)
    $repoPrefix = $resolvedRepo + [System.IO.Path]::DirectorySeparatorChar
    if (
        $resolvedRoot.Equals($resolvedRepo, [System.StringComparison]::OrdinalIgnoreCase) -or
        $resolvedRoot.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)
    ) {
        throw "PytestBaseTempRoot must remain outside the repository."
    }
    if (-not (Test-Path -LiteralPath $resolvedRoot -PathType Container)) {
        throw "PytestBaseTempRoot must be an existing directory."
    }

    # A normal leaf below a Junction is still an aliased location. Inspect
    # the lexical ancestor chain without creating or repairing any directory.
    $currentPath = $resolvedRoot
    while ($true) {
        $rootItem = Get-Item -LiteralPath $currentPath -Force
        if (($rootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "PytestBaseTempRoot must not be a reparse point or have reparse-point ancestors."
        }
        $parentDirectory = [System.IO.Directory]::GetParent($currentPath)
        if ($null -eq $parentDirectory) {
            break
        }
        $currentPath = $parentDirectory.FullName
    }

    $runLeaf = Join-Path $resolvedRoot (
        "pytest-{0}-{1}-{2}" -f
        $Lane.ToLowerInvariant(),
        $PID,
        [Guid]::NewGuid().ToString("N")
    )
    if (Test-Path -LiteralPath $runLeaf) {
        throw "Unable to allocate a non-existent pytest basetemp path."
    }
    return $runLeaf
}

if ($Json -and -not $EnvironmentOnly) {
    try {
        $RunResult.wrapper_sha256 = Get-Sha256Hex -LiteralPath $PSCommandPath
    } catch {
        Stop-SetupFailure -ReasonCode "WRAPPER_HASH_UNAVAILABLE" -TextMessage $_.Exception.Message
    }
}

try {
    Set-Location -LiteralPath $RepoRoot
} catch {
    Stop-SetupFailure -ReasonCode "REPOSITORY_SETUP_FAILED" -TextMessage $_.Exception.Message
}

$PytestBaseTempPath = $null
$PytestBaseTempReadiness = "OS_DEFAULT_UNVERIFIED"
$PytestBaseTempReason = $null
if ($PSBoundParameters.ContainsKey("PytestBaseTempRoot")) {
    try {
        $PytestBaseTempPath = New-PytestBaseTempPath -Root $PytestBaseTempRoot
        $PytestBaseTempReadiness = "READY"
    } catch {
        if (-not $EnvironmentOnly) {
            Stop-SetupFailure -ReasonCode "PYTEST_BASETEMP_ROOT_INVALID" -TextMessage $_.Exception.Message
        }
        $PytestBaseTempReadiness = "BLOCKED"
        $PytestBaseTempReason = "PYTEST_BASETEMP_ROOT_INVALID"
    }
}

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

try {
    Set-HermeticVerificationEnvironment
} catch {
    Stop-SetupFailure -ReasonCode "HEREMETIC_ENVIRONMENT_SETUP_FAILED" -TextMessage $_.Exception.Message
}

function Find-Python {
    param([switch]$Diagnostic)

    $candidates = @()
    $candidateClasses = @()
    if ($env:PYTHON) {
        $candidates += $env:PYTHON
        $candidateClasses += "explicit_env"
    }

    $repoVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $repoVenvPython) {
        $candidates += $repoVenvPython
        $candidateClasses += "repo_venv"
    }

    $candidates += "python"
    $candidateClasses += "system_python"
    $candidates += "py"
    $candidateClasses += "py_launcher"

    $codexPython = Join-Path $HOME ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $codexPython) {
        $candidates += $codexPython
        $candidateClasses += "codex_bundled"
    }

    $identityArgs = @()
    if ($Diagnostic) {
        $identityArgs += "--runtime-identity"
    }
    for ($index = 0; $index -lt $candidates.Count; $index++) {
        $candidate = $candidates[$index]
        try {
            $global:LASTEXITCODE = $null
            if ($candidate -eq "py") {
                $checkerOutput = & py -3.12 scripts/verify_dev_environment.py --expected-version-file .python-version --lock requirements-dev.lock --json @identityArgs 2>$null
            } else {
                $checkerOutput = & $candidate scripts/verify_dev_environment.py --expected-version-file .python-version --lock requirements-dev.lock --json @identityArgs 2>$null
            }
            $checkerExitCode = $global:LASTEXITCODE
            if ($null -ne $checkerExitCode -and [int]$checkerExitCode -eq 0) {
                if ($Diagnostic) {
                    try {
                        $checker = ($checkerOutput -join "`n") | ConvertFrom-Json
                    } catch {
                        continue
                    }
                    return [PSCustomObject]@{
                        Command = $candidate
                        CandidateClass = $candidateClasses[$index]
                        Checker = $checker
                    }
                }
                return $candidate
            }
        } catch {
            continue
        }
    }

    throw "No Python candidate satisfies .python-version and requirements-dev.lock. Install the exact development environment or set PYTHON."
}

if ($EnvironmentOnly) {
    $reasonCodes = New-Object System.Collections.Generic.List[string]
    if ($null -ne $PytestBaseTempReason) {
        $reasonCodes.Add($PytestBaseTempReason)
    }

    $selection = $null
    try {
        $selection = Find-Python -Diagnostic
    } catch {
        $reasonCodes.Add("NO_COMPATIBLE_PYTHON_CANDIDATE")
    }

    $shellIdentity = $null
    if ($null -ne $selection) {
        try {
            $shellPath = [System.Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
            $shellHash = Get-Sha256Hex -LiteralPath $shellPath
            $shellKind = if ($PSVersionTable.PSEdition -eq "Desktop") {
                "winps"
            } else {
                "pwsh"
            }
            $shellIdentity = [PSCustomObject]@{
                Kind = $shellKind
                Version = $PSVersionTable.PSVersion.ToString()
                Hash = $shellHash
            }
        } catch {
            $reasonCodes.Add("SHELL_IDENTITY_UNAVAILABLE")
        }
    }

    $candidateClass = "NONE"
    $interpreterId = "UNKNOWN"
    $executableHash = "UNKNOWN"
    $pytestVersion = "UNKNOWN"
    $expectedVersion = "UNKNOWN"
    $observedVersion = "UNKNOWN"
    $lockCount = 0
    $matchedLockCount = 0
    $pipCheck = "NOT RUN"
    if ($null -ne $selection) {
        $candidateClass = $selection.CandidateClass
        $environment = $selection.Checker.environment
        $identity = $selection.Checker.runtime_identity
        $expectedVersion = $environment.expected_python_version
        $observedVersion = $environment.observed_python_version
        $lockCount = $environment.lock_package_count
        $matchedLockCount = $environment.matched_lock_package_count
        $pipCheck = $environment.pip_check
        if ($null -eq $identity) {
            $reasonCodes.Add("RUNTIME_IDENTITY_UNAVAILABLE")
        } else {
            $executableHash = $identity.executable_sha256
            $pytestVersion = $identity.pytest_version
            if ($null -ne $shellIdentity) {
                $safePytestVersion = (
                    [string]$identity.pytest_version
                ).ToLowerInvariant() -replace '[^a-z0-9._-]', '-'
                $interpreterId = (
                    "py{0}-pytest{1}-{2}-{3}{4}-{5}" -f
                    $observedVersion,
                    $safePytestVersion,
                    $executableHash.Substring(0, 10),
                    $shellIdentity.Kind,
                    $shellIdentity.Version,
                    $shellIdentity.Hash.Substring(0, 10)
                )
                if (
                    $interpreterId.Length -gt 64 -or
                    $interpreterId -notmatch '^[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?$'
                ) {
                    $interpreterId = "UNKNOWN"
                    $reasonCodes.Add("INTERPRETER_ID_INVALID")
                }
            }
        }
    }

    $diagnosticStatus = if ($null -eq $selection) {
        "ENVIRONMENT BLOCKED"
    } elseif ($reasonCodes.Count -eq 0) {
        "PASS"
    } else {
        "FAIL"
    }
    $result = [ordered]@{
        schema_version = "1"
        checker_id = "local_verify_environment_diagnostic"
        status = $diagnosticStatus
        reason_codes = @($reasonCodes | Sort-Object -Unique)
        candidate_class = $candidateClass
        interpreter_id = $interpreterId
        executable_sha256 = $executableHash
        pytest_version = $pytestVersion
        expected_python_version = $expectedVersion
        observed_python_version = $observedVersion
        lock_package_count = $lockCount
        matched_lock_package_count = $matchedLockCount
        pip_check = $pipCheck
        basetemp_readiness = $PytestBaseTempReadiness
        performed_actions = @()
    }
    if ($Json) {
        Write-Output ($result | ConvertTo-Json -Compress -Depth 4)
    } else {
        Write-Output (
            "{0}: candidate={1} python={2} lock={3}/{4} pip={5} basetemp={6}" -f
            $diagnosticStatus,
            $candidateClass,
            $observedVersion,
            $matchedLockCount,
            $lockCount,
            $pipCheck,
            $PytestBaseTempReadiness
        )
    }
    if ($diagnosticStatus -eq "PASS") {
        exit 0
    }
    exit 1
}

try {
    $PythonCommand = Find-Python
} catch {
    Stop-SetupFailure -ReasonCode "PYTHON_SELECTION_FAILED" -TextMessage $_.Exception.Message
}

function Invoke-PythonStep {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string[]]$PythonArgs
    )

    $step = $RunResult.steps[$script:NextStepIndex]
    $actualInvocation = if ($PythonCommand -eq "py") {
        @([string]$PythonCommand, "-3.12") + @($PythonArgs)
    } else {
        @([string]$PythonCommand) + @($PythonArgs)
    }
    $safeInvocation = if ($PythonCommand -eq "py") {
        @("{PY_LAUNCHER}", "-3.12") + @($PythonArgs)
    } else {
        @("{PYTHON}") + @($PythonArgs)
    }
    if ($null -ne $PytestBaseTempPath) {
        $safeInvocation = @(
            $safeInvocation | ForEach-Object {
                if ([string]$_ -ceq $PytestBaseTempPath) {
                    "{PYTEST_BASETEMP}"
                } else {
                    [string]$_
                }
            }
        )
    }

    try {
        $invocationHash = Get-InvocationSha256Hex -Tokens $actualInvocation
    } catch {
        $step.status = "FAIL"
        $step.reason_codes = @("INVOCATION_EVIDENCE_FAILED")
        Add-RunReasonCode -ReasonCode "INVOCATION_EVIDENCE_FAILED"
        if ($Json) {
            Complete-ExecutionResult -ExitCode 1
        }
        [Console]::Error.WriteLine("$Label failed before invocation.")
        exit 1
    }
    $step.safe_argv = @($safeInvocation)
    $step.invocation_sha256 = $invocationHash

    if (-not $Json) {
        Write-Host "==> $Label"
    }
    $executable = $actualInvocation[0]
    $arguments = @($actualInvocation[1..($actualInvocation.Count - 1)])
    $observedExitCode = $null
    $launchFailed = $false
    $priorErrorActionPreference = $ErrorActionPreference
    $global:LASTEXITCODE = $null
    try {
        if ($Json) {
            $ErrorActionPreference = "Continue"
            & $executable @arguments 2>&1 | ForEach-Object {
                [Console]::Error.WriteLine([string]$_)
            }
        } else {
            & $executable @arguments
        }
        $observedExitCode = $global:LASTEXITCODE
    } catch {
        $launchFailed = $true
    } finally {
        $ErrorActionPreference = $priorErrorActionPreference
    }

    if ($launchFailed) {
        $step.status = "FAIL"
        $step.reason_codes = @("STEP_LAUNCH_FAILED")
        Add-RunReasonCode -ReasonCode "STEP_LAUNCH_FAILED"
        if ($Json) {
            Complete-ExecutionResult -ExitCode 1
        }
        [Console]::Error.WriteLine("$Label failed to launch.")
        exit 1
    }
    if ($null -eq $observedExitCode) {
        $step.status = "FAIL"
        $step.reason_codes = @("STEP_EXIT_CODE_UNAVAILABLE")
        Add-RunReasonCode -ReasonCode "STEP_EXIT_CODE_UNAVAILABLE"
        if ($Json) {
            Complete-ExecutionResult -ExitCode 1
        }
        [Console]::Error.WriteLine("$Label did not report an exit code.")
        exit 1
    }

    $step.exit_code = [int]$observedExitCode
    if ([int]$observedExitCode -ne 0) {
        $step.status = "FAIL"
        $step.reason_codes = @("CHILD_EXIT_NONZERO")
        Add-RunReasonCode -ReasonCode "CHILD_EXIT_NONZERO"
        if ($Json) {
            Complete-ExecutionResult -ExitCode ([int]$observedExitCode)
        }
        [Console]::Error.WriteLine(
            "$Label failed with exit code $observedExitCode"
        )
        exit ([int]$observedExitCode)
    }

    $step.status = "PASS"
    $script:NextStepIndex++
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

$PytestArgs = @("-m", "pytest", "tests", "--durations=50", "-rs", "-p", "no:cacheprovider")
if ($null -ne $PytestBaseTempPath) {
    $PytestArgs += @("--basetemp", $PytestBaseTempPath)
}
if ($Lane -eq "Routine") {
    foreach ($heldTestFile in $RoutineHeldTestFiles) {
        $heldTestPath = Join-Path $RepoRoot $heldTestFile
        if (-not (Test-Path -LiteralPath $heldTestPath -PathType Leaf)) {
            Stop-SetupFailure -ReasonCode "ROUTINE_INVENTORY_INVALID" -TextMessage "Routine held test file is missing: $heldTestFile"
        }
        $PytestArgs += @("--ignore", $heldTestFile)
    }
}
elseif ($Lane -eq "Core") {
    $PytestArgs += @(
        "-m",
        "not optional_agent_quality and not optional_hermes_mcp and not optional_local_rag"
    )
}

if (-not $Json) {
    Write-Host "Local verification lane: $Lane"
    if ($null -ne $PytestBaseTempPath) {
        Write-Host "Pytest basetemp: $PytestBaseTempPath"
    }
}
$script:NextStepIndex = 0
Invoke-PythonStep "development environment" @("scripts/verify_dev_environment.py", "--expected-version-file", ".python-version", "--lock", "requirements-dev.lock", "--json")
Invoke-PythonStep "pytest" $PytestArgs
Invoke-PythonStep "standalone eval" @("scripts/run_eval.py")
Invoke-PythonStep "quality gate" @("scripts/quality_gate.py")
Invoke-PythonStep "python_cli_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/python_cli_minimal/template.config.yml", "--target", "examples/python_cli_minimal", "--dry-run")
Invoke-PythonStep "csharp_desktop_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/csharp_desktop_minimal/template.config.yml", "--target", "examples/csharp_desktop_minimal", "--dry-run")
Invoke-PythonStep "plc_tool_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/plc_tool_minimal/template.config.yml", "--target", "examples/plc_tool_minimal", "--dry-run")

if ($Json) {
    Complete-ExecutionResult -ExitCode 0
}
Write-Host "Local verification passed ($Lane)."
