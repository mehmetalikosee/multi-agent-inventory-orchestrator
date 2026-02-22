# Run the Autonomous Business Logic Orchestrator
# Usage: .\run.ps1   or   .\run.ps1 test

param([string]$Mode = "main")

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($Mode -eq "test") {
    python run_tests.py
    exit $LASTEXITCODE
}

python main.py
exit $LASTEXITCODE
