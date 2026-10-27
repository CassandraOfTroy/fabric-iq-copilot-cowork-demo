<#
.SYNOPSIS
    Fails fast unless the repo-isolated Azure CLI profile is signed in to the tenant in config/tenant.json.

.DESCRIPTION
    Call this at the top of EVERY script that touches Azure or Fabric. It checks both the active
    Azure CLI account and the tenant claim (tid) inside a real Fabric API token, so a wrong-tenant
    call can never reach the Fabric REST API.

.OUTPUTS
    Writes the signed-in UPN and tenant on success; throws on any mismatch.
#>
[CmdletBinding()]
param([switch]$Quiet)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Use-CaldovaTenant.ps1') -Quiet

$acctJson = az account show --output json 2>$null
if ($LASTEXITCODE -ne 0 -or -not $acctJson) {
    throw '[CALDOVA] Not signed in. Run ./scripts/Connect-Caldova.ps1'
}
$acct = $acctJson | ConvertFrom-Json
if ($acct.tenantId -ne $cfg.tenantId) {
    throw "[CALDOVA] WRONG TENANT '$($acct.tenantId)'. Expected $($cfg.tenantDomain) ($($cfg.tenantId)). Aborting."
}

$token = az account get-access-token --resource 'https://api.fabric.microsoft.com' --tenant $cfg.tenantId --query accessToken --output tsv
if ($LASTEXITCODE -ne 0 -or -not $token) { throw '[CALDOVA] Could not get a Fabric token for the configured tenant.' }

$payload = $token.Split('.')[1].Replace('-', '+').Replace('_', '/')
switch ($payload.Length % 4) { 2 { $payload += '==' } 3 { $payload += '=' } }
$claims = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($payload)) | ConvertFrom-Json
if ($claims.tid -ne $cfg.tenantId) {
    throw "[CALDOVA] Fabric token was issued by tenant '$($claims.tid)', not $($cfg.tenantDomain). Aborting."
}

$who = if ($claims.upn) { $claims.upn } elseif ($claims.unique_name) { $claims.unique_name } else { $acct.user.name }
if (-not $Quiet) {
    Write-Host "[CALDOVA] OK - signed in as $who, tenant $($cfg.tenantDomain) ($($claims.tid))" -ForegroundColor Green
}
[pscustomobject]@{ User = $who; TenantId = $claims.tid; TenantDomain = $cfg.tenantDomain }
