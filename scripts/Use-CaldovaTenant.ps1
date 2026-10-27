<#
.SYNOPSIS
    Pins the CURRENT PowerShell session to the demo tenant in config/tenant.json.

.DESCRIPTION
    Dot-source this file:   . .\scripts\Use-CaldovaTenant.ps1

    It points the Azure CLI at a repo-local profile folder (azureConfigDir in config/tenant.json, git-ignored)
    through AZURE_CONFIG_DIR, so `az login`, `az account set` and every token used in this session live in
    that folder and NEVER touch your default/corporate Azure CLI profile (%USERPROFILE%\.azure).
    It also pins Azure-Identity based tools (Fabric MCP server, Python azure-identity) to the
    Azure CLI credential and the configured tenant ID.

    Grounding: https://learn.microsoft.com/cli/azure/use-azure-cli-successfully-tips (Concurrent execution / AZURE_CONFIG_DIR)
               https://learn.microsoft.com/cli/azure/azure-cli-configuration
#>
[CmdletBinding()]
param([switch]$Quiet)

$repoRoot   = Split-Path -Parent $PSScriptRoot
$configFile = Join-Path $repoRoot 'config\tenant.json'
if (-not (Test-Path $configFile)) {
    throw "[CALDOVA] $configFile not found. Copy config\tenant.example.json to config\tenant.json and fill in your tenant (tenantId, tenantDomain, Fabric capacity). config\tenant.json is git-ignored."
}
$cfg = Get-Content $configFile -Raw | ConvertFrom-Json
if (-not $cfg.tenantId -or $cfg.tenantId -like '00000000-*' -or -not $cfg.tenantDomain -or $cfg.tenantDomain -like '*<*') {
    throw '[CALDOVA] config\tenant.json still has placeholder values: set tenantId and tenantDomain to your tenant.'
}
$configDir = Join-Path $repoRoot $cfg.azureConfigDir
if (-not (Test-Path $configDir)) { New-Item -ItemType Directory -Path $configDir | Out-Null }

$env:AZURE_CONFIG_DIR        = $configDir
$env:AZURE_TENANT_ID         = $cfg.tenantId
$env:AZURE_TOKEN_CREDENTIALS = 'AzureCliCredential'
$env:CALDOVA_REPO_ROOT       = $repoRoot
$env:CALDOVA_TENANT_ID       = $cfg.tenantId

if (-not $Quiet) {
    Write-Host "[CALDOVA] Session pinned to tenant $($cfg.tenantDomain) ($($cfg.tenantId))" -ForegroundColor Magenta
    Write-Host "[CALDOVA] AZURE_CONFIG_DIR = $configDir" -ForegroundColor Magenta
}
