Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $RepoRoot

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
    $candidates += "python"
    $candidates += "py"

    $codexPython = Join-Path $HOME ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $codexPython) {
        $candidates += $codexPython
    }

    foreach ($candidate in $candidates) {
        try {
            if ($candidate -eq "py") {
                & py -3 --version *> $null
            } else {
                & $candidate --version *> $null
            }
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        } catch {
            continue
        }
    }

    throw "Python was not found. Install Python or set the PYTHON environment variable."
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
        & py -3 @PythonArgs
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

function Write-ArtifactPaths {
    $artifactPaths = @(
        "artifacts/release-manifest.json",
        "artifacts/checksums.sha256",
        "artifacts/sbom.spdx.json",
        "artifacts/sbom.cdx.json",
        "artifacts/provenance.intoto.jsonl"
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

Invoke-PowerShellStep "local verification wrapper" (Join-Path $RepoRoot "scripts/run_local_verify.ps1")

$PythonCommand = Find-Python

Invoke-OptionalPythonScript "optional eval" (Join-Path $RepoRoot "scripts/run_eval.py") @("scripts/run_eval.py")
Invoke-PythonStep "release manifest generation" @("scripts/generate_manifest.py", "--output", $ManifestPath)
Invoke-PythonStep "checksum generation" @("scripts/generate_checksums.py", "--manifest", $ManifestPath, "--output", $ChecksumsPath, "--allow-missing")
Invoke-OptionalPythonScript "optional SBOM generation" (Join-Path $RepoRoot "scripts/generate_sbom.py") @("scripts/generate_sbom.py", "--manifest", $ManifestPath, "--spdx", $SpdxPath, "--cyclonedx", $CycloneDxPath)
Invoke-OptionalPythonScript "optional provenance generation" (Join-Path $RepoRoot "scripts/generate_provenance.py") @("scripts/generate_provenance.py", "--manifest", $ManifestPath, "--output", $ProvenancePath)
Invoke-PythonStep "final checksum regeneration" @("scripts/generate_checksums.py", "--manifest", $ManifestPath, "--output", $ChecksumsPath)
Invoke-PythonStep "checksum verification" @("scripts/generate_checksums.py", "--verify")

Write-ArtifactPaths
Write-Summary
Write-Host "Release verification passed."
