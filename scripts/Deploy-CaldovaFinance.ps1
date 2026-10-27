<#
.SYNOPSIS
    Deploys the Caldova Finance demo (supplier invoice assurance) to the tenant in config/tenant.json ONLY.
.DESCRIPTION
    Pins the session to the repo-local Azure CLI profile, asserts the configured tenant, then runs
    scripts/deploy/deploy_finance.py. Steps, in order:
      workspaces   resolve or create 'Caldova Finance' + 'Caldova Finance Insights' and LH_CaldovaFinance; workspace roles
      load         data/finance/*.csv -> Delta tables in the lakehouse
      model        Direct Lake semantic model 'Supplier Invoice Assurance' from fabric/ (TMDL)
      refresh      lakehouse metadata sync + model reframe
      connection   fixed identity (workspace identity, SSO off) for the Direct Lake connection
      permissions  IsaacF and ColinB Read + Build on the model
      reports      PBIR report 'Supplier Invoice Assurance' -> 'Caldova Finance Insights'
      validate     DAX checks against data/finance/expected_answers.json (+ Colin's RLS view)
    RLS role members are never scripted: add IsaacF to 'Region Manager' and ColinB to 'Business User'
    in the Power BI service.
    Manual steps (Prep data for AI, seeding, rehearsal) are in README.md.
.EXAMPLE
    pwsh -File scripts\Deploy-CaldovaFinance.ps1                          # all steps
    pwsh -File scripts\Deploy-CaldovaFinance.ps1 -Step load,refresh       # reload data and reframe
    pwsh -File scripts\Deploy-CaldovaFinance.ps1 -Step validate           # DAX + RLS checks
#>
[CmdletBinding()]
param(
    # One or more of: all, workspaces, load, model, refresh, connection, permissions, reports, validate
    [string[]]$Step = @('all'),
    # Pushes local TMDL changes to an existing model.
    [switch]$UpdateModel,
    # Overwrites the already-published report with the local PBIR.
    [switch]$UpdateReports
)
$ErrorActionPreference = 'Stop'
$valid = 'all', 'workspaces', 'load', 'model', 'refresh', 'connection', 'permissions', 'reports', 'validate'
$Step = @($Step | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$bad = $Step | Where-Object { $_ -notin $valid }
if ($bad) { throw "Unknown step(s): $($bad -join ', '). Valid: $($valid -join ', ')" }
. (Join-Path $PSScriptRoot 'Use-CaldovaTenant.ps1')
& (Join-Path $PSScriptRoot 'Assert-CaldovaTenant.ps1') | Out-Null

$python = Join-Path $env:CALDOVA_REPO_ROOT '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw "Python venv missing: create it with 'py -3.11 -m venv .venv' and '.venv\Scripts\pip install -r requirements.txt'" }
$pyArgs = @((Join-Path $PSScriptRoot 'deploy\deploy_finance.py'), '--steps', ($Step -join ','))
if ($UpdateModel) { $pyArgs += '--update-model' }
if ($UpdateReports) { $pyArgs += '--update-reports' }
& $python @pyArgs
if ($LASTEXITCODE -ne 0) { throw "Finance deployment failed (exit $LASTEXITCODE)" }
