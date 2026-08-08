Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $RepoRoot

function Clear-AmbientVerificationEnvironment {
    foreach ($name in @("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH")) {
        [Environment]::SetEnvironmentVariable(
            $name,
            $null,
            [EnvironmentVariableTarget]::Process
        )
    }
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
}

Clear-AmbientVerificationEnvironment

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
                & py -3 scripts/verify_dev_environment.py --expected-version-file .python-version --lock requirements-dev.lock --json *> $null
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
        & py -3 @PythonArgs
    } else {
        & $PythonCommand @PythonArgs
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Error "$Label failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

Invoke-PythonStep "development environment" @("scripts/verify_dev_environment.py", "--expected-version-file", ".python-version", "--lock", "requirements-dev.lock", "--json")
Invoke-PythonStep "pytest" @("-m", "pytest", "tests", "--durations=50", "-rs")
Invoke-PythonStep "standalone eval" @("scripts/run_eval.py")
Invoke-PythonStep "quality gate" @("scripts/quality_gate.py")
Invoke-PythonStep "python_cli_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/python_cli_minimal/template.config.yml", "--target", "examples/python_cli_minimal", "--dry-run")
Invoke-PythonStep "csharp_desktop_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/csharp_desktop_minimal/template.config.yml", "--target", "examples/csharp_desktop_minimal", "--dry-run")
Invoke-PythonStep "plc_tool_minimal render dry-run" @("scripts/render_template.py", "--config", "examples/plc_tool_minimal/template.config.yml", "--target", "examples/plc_tool_minimal", "--dry-run")

Write-Host "Local verification passed."
