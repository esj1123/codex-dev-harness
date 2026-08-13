param(
    [ValidateSet("Local", "GitHubActionsManualExport")]
    [string]$EvidenceContext = "Local"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $RepoRoot

function Set-HermeticGitEnvironment {
    $ambientNames = @(
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

Set-HermeticGitEnvironment

$Results = New-Object System.Collections.Generic.List[object]

function Add-Result {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$Detail
    )

    $Results.Add([pscustomobject]@{
        Label = $Label
        Status = $Status
        Detail = $Detail
    }) | Out-Null
}

function Write-Summary {
    Write-Host "==> Release verification summary"
    foreach ($result in $Results) {
        Write-Host ("[{0}] {1} - {2}" -f $result.Status, $result.Label, $result.Detail)
    }
}

function Fail-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$Detail,
        [int]$ExitCode = 1
    )

    Add-Result $Label "FAIL" $Detail
    Write-Summary
    exit $ExitCode
}

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

function Invoke-PowerShellStep {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$ScriptPath
    )

    if (-not (Test-Path -LiteralPath $ScriptPath)) {
        Fail-Step $Label "missing script: $ScriptPath"
    }

    Write-Host "==> $Label"
    & powershell -NoProfile -ExecutionPolicy Bypass -File $ScriptPath
    if ($LASTEXITCODE -ne 0) {
        Fail-Step $Label "exit code $LASTEXITCODE" $LASTEXITCODE
    }
    Add-Result $Label "PASS" $ScriptPath
}

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
        Fail-Step $Label "exit code $LASTEXITCODE" $LASTEXITCODE
    }

    Add-Result $Label "PASS" ("python {0}" -f ($PythonArgs -join " "))
}

function Invoke-OptionalPythonScript {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$ScriptPath,
        [Parameter(Mandatory = $true)][string[]]$PythonArgs
    )

    if (-not (Test-Path -LiteralPath $ScriptPath)) {
        Add-Result $Label "SKIPPED" "missing optional script: $ScriptPath"
        Write-Host "==> $Label"
        Write-Host "SKIPPED: missing optional script: $ScriptPath"
        return
    }

    Invoke-PythonStep $Label $PythonArgs
}

function Assert-CleanGitTree {
    $status = & git status --porcelain=v1 --untracked-files=all
    if ($LASTEXITCODE -ne 0) {
        Fail-Step "clean Git tree" "unable to inspect repository state" $LASTEXITCODE
    }
    if ($status) {
        Fail-Step "clean Git tree" "tracked or untracked changes are present"
    }
    Add-Result "clean Git tree" "PASS" "HEAD source basis is clean"
}

function Assert-EvidenceContext {
    if ($EvidenceContext -eq "Local") {
        return
    }
    if ($env:GITHUB_ACTIONS -cne "true") {
        Fail-Step "evidence context" "GitHubActionsManualExport requires GITHUB_ACTIONS=true"
    }
    if ($env:GITHUB_EVENT_NAME -cne "workflow_dispatch") {
        Fail-Step "evidence context" "GitHubActionsManualExport requires workflow_dispatch"
    }
    if ($env:GITHUB_SHA -cnotmatch '^[0-9a-f]{40}$') {
        Fail-Step "evidence context" "GitHubActionsManualExport requires a lowercase GITHUB_SHA"
    }
    $headCommit = & git rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $headCommit -cne $env:GITHUB_SHA) {
        Fail-Step "evidence context" "GITHUB_SHA does not match HEAD"
    }
    Add-Result "evidence context" "PASS" "github_actions_manual_export"
}

function Write-ArtifactPaths {
    $artifactPaths = @(
        "artifacts/release-manifest.json",
        "artifacts/checksums.sha256",
        "artifacts/sbom.spdx.json",
        "artifacts/sbom.cdx.json",
        "artifacts/provenance.intoto.jsonl",
        "artifacts/eval-report.json"
    )

    Write-Host "==> Release evidence artifacts"
    foreach ($relativePath in $artifactPaths) {
        $path = Join-Path $RepoRoot $relativePath
        if (Test-Path -LiteralPath $path) {
            Write-Host ("[PRESENT] {0}" -f $relativePath)
        } else {
            Write-Host ("[MISSING] {0}" -f $relativePath)
        }
    }
}

$ManifestPath = "artifacts/release-manifest.json"
$ChecksumsPath = "artifacts/checksums.sha256"
$SpdxPath = "artifacts/sbom.spdx.json"
$CycloneDxPath = "artifacts/sbom.cdx.json"
$ProvenancePath = "artifacts/provenance.intoto.jsonl"
$EvalReportPath = "artifacts/eval-report.json"

$PythonCommand = Find-Python
$env:PYTHON = $PythonCommand

Assert-EvidenceContext
Assert-CleanGitTree
Invoke-PowerShellStep "local verification wrapper" (Join-Path $RepoRoot "scripts/run_local_verify.ps1")

Invoke-PythonStep "release manifest generation" @("scripts/generate_manifest.py", "--output", $ManifestPath)
if (Test-Path -LiteralPath (Join-Path $RepoRoot $EvalReportPath) -PathType Leaf) {
    Invoke-PythonStep "optional eval report refresh" @("scripts/run_eval.py", "--report", $EvalReportPath)
} else {
    Add-Result "optional eval report refresh" "SKIPPED" "optional eval report is absent"
}
Invoke-OptionalPythonScript "optional SBOM generation" (Join-Path $RepoRoot "scripts/generate_sbom.py") @("scripts/generate_sbom.py", "--manifest", $ManifestPath, "--spdx", $SpdxPath, "--cyclonedx", $CycloneDxPath)
$ProvenanceArgs = @("scripts/generate_provenance.py", "--manifest", $ManifestPath, "--output", $ProvenancePath)
if ($EvidenceContext -eq "GitHubActionsManualExport") {
    $ProvenanceArgs += @("--execution-context", "github_actions_manual_export")
}
Invoke-OptionalPythonScript "optional provenance generation" (Join-Path $RepoRoot "scripts/generate_provenance.py") $ProvenanceArgs
Invoke-PythonStep "final checksum generation" @("scripts/generate_checksums.py", "--manifest", $ManifestPath, "--output", $ChecksumsPath)
Invoke-PythonStep "checksum verification" @("scripts/generate_checksums.py", "--verify")

Write-ArtifactPaths
Write-Summary
Write-Host "Release verification passed."
