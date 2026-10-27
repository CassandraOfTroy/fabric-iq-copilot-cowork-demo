<#
.SYNOPSIS
    Optional, after the demo (not a demo step): Laurence's fix at the source - update a contract price and refresh the model.
.DESCRIPTION
    Pins the session to the repo-local Azure CLI profile, asserts the configured tenant, then runs
    scripts/deploy/update_contract_price.py. Laurence Gilbertson (Data Analyst, Contributor on 'Caldova Finance')
    registers the price from the signed amendment in the contract data, and the semantic model is refreshed:
    Germany is back to 100%. -Reset returns to the demo start (amendment not registered).
.EXAMPLE
    pwsh -File scripts\Update-CaldovaContractPrice.ps1 -Contract CTR-ANN-DE -UnitPrice 4.45 -ValidFrom 2026-10-05
.EXAMPLE
    pwsh -File scripts\Update-CaldovaContractPrice.ps1 -Reset
#>
[CmdletBinding(DefaultParameterSetName = 'Update')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Update')][string]$Contract,
    [Parameter(Mandatory, ParameterSetName = 'Update')][decimal]$UnitPrice,
    [Parameter(Mandatory, ParameterSetName = 'Update')][string]$ValidFrom,
    [Parameter(Mandatory, ParameterSetName = 'Reset')][switch]$Reset
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Use-CaldovaTenant.ps1')
& (Join-Path $PSScriptRoot 'Assert-CaldovaTenant.ps1') | Out-Null

$python = Join-Path $env:CALDOVA_REPO_ROOT '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw "Python venv missing: create it with 'py -3.11 -m venv .venv' and '.venv\Scripts\pip install -r requirements.txt'" }
$pyArgs = @((Join-Path $PSScriptRoot 'deploy\update_contract_price.py'))
if ($Reset) { $pyArgs += '--reset' }
else { $pyArgs += @('--contract', $Contract, '--price', $UnitPrice.ToString([cultureinfo]::InvariantCulture), '--valid-from', $ValidFrom) }
& $python @pyArgs
if ($LASTEXITCODE -ne 0) { throw "Contract price update failed (exit $LASTEXITCODE)" }
