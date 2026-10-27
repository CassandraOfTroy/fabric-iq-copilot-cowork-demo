<#
.SYNOPSIS
    Signs in to the demo tenant inside the repo-isolated Azure CLI profile.

.DESCRIPTION
    Default = device code flow. Open the printed URL in an InPrivate browser window (or the browser
    profile of the demo user) and sign in with the demo-tenant account. Nothing is written to your
    default/corporate Azure CLI profile (%USERPROFILE%\.azure), so your login in other repos stays exactly as it is.

    No credential is ever stored or passed on the command line - sign-in is interactive (MFA).

.PARAMETER Interactive
    Use the browser / Windows account picker (WAM) instead of device code. Pick the demo-tenant account
    (or "Use another account") - not your corporate account.

.EXAMPLE
    ./scripts/Connect-Caldova.ps1
.EXAMPLE
    ./scripts/Connect-Caldova.ps1 -Interactive
#>
[CmdletBinding()]
param([switch]$Interactive)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Use-CaldovaTenant.ps1')

Write-Host ''
Write-Host "Sign in with an account of $($cfg.tenantDomain) that can deploy Fabric content, for example:" -ForegroundColor Cyan
Write-Host "  data analyst   : $($cfg.users.dataAnalyst)@$($cfg.tenantDomain)   (Admin on both finance workspaces)" -ForegroundColor Cyan
Write-Host "  or the tenant admin account that owns the Fabric capacity" -ForegroundColor Cyan
Write-Host ''

$loginArgs = @('login', '--tenant', $cfg.tenantId, '--allow-no-subscriptions', '--output', 'none')
if (-not $Interactive) { $loginArgs += '--use-device-code' }
az @loginArgs
if ($LASTEXITCODE -ne 0) { throw '[CALDOVA] az login failed.' }

# Select the demo subscription when the signed-in user can see it (tenant admin).
# Fabric-only users have no Azure subscription - that is expected and fine.
$subs = @(az account list --query "[?tenantId=='$($cfg.tenantId)'].id" --output tsv)
if ($cfg.subscriptionId -and $subs -contains $cfg.subscriptionId) {
    az account set --subscription $cfg.subscriptionId --output none
}

& (Join-Path $PSScriptRoot 'Assert-CaldovaTenant.ps1')
