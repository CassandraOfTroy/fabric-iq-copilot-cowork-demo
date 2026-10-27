<#
.SYNOPSIS
    Proves the tenant isolation: your DEFAULT Azure CLI profile vs. this repo's demo-tenant profile.

.DESCRIPTION
    Read-only. Runs `az account show` twice - once against the default profile
    (%USERPROFILE%\.azure, used by your other repos) and once against the repo-local
    profile (azureConfigDir in config/tenant.json) - and checks that:
      1. the repo-local profile folder is git-ignored (tokens can never be committed)
      2. the default profile is NOT pointed at the demo tenant (your default/corporate login is untouched)
      3. the repo-local profile IS pointed at the demo tenant (after Connect-Caldova.ps1)
#>
[CmdletBinding()]
param()

$repoRoot   = Split-Path -Parent $PSScriptRoot
$configFile = Join-Path $repoRoot 'config\tenant.json'
if (-not (Test-Path $configFile)) {
    throw "[CALDOVA] $configFile not found. Copy config\tenant.example.json to config\tenant.json and fill in your tenant."
}
$cfg       = Get-Content $configFile -Raw | ConvertFrom-Json
$demoDir   = Join-Path $repoRoot $cfg.azureConfigDir

function Get-AzProfileContext {
    param([string]$ConfigDir)
    $saved = $env:AZURE_CONFIG_DIR
    try {
        if ($ConfigDir) { $env:AZURE_CONFIG_DIR = $ConfigDir } else { Remove-Item Env:AZURE_CONFIG_DIR -ErrorAction SilentlyContinue }
        $json = az account show --query '{user:user.name, tenantId:tenantId, subscription:name}' --output json 2>$null
        if ($LASTEXITCODE -eq 0 -and $json) { $json | ConvertFrom-Json } else { $null }
    }
    finally {
        if ($null -ne $saved) { $env:AZURE_CONFIG_DIR = $saved } else { Remove-Item Env:AZURE_CONFIG_DIR -ErrorAction SilentlyContinue }
    }
}

$default = Get-AzProfileContext -ConfigDir ''
$demo    = if (Test-Path $demoDir) { Get-AzProfileContext -ConfigDir $demoDir } else { $null }

Push-Location $repoRoot
git check-ignore -q "$($cfg.azureConfigDir)/azureProfile.json" 2>$null
$ignored = ($LASTEXITCODE -eq 0)
git check-ignore -q 'config/tenant.json' 2>$null
$configIgnored = ($LASTEXITCODE -eq 0)
Pop-Location

$rows = @(
    [pscustomobject]@{ Profile = 'DEFAULT (%USERPROFILE%\.azure)'; User = $default.user; Tenant = $default.tenantId; Subscription = $default.subscription }
    [pscustomobject]@{ Profile = "DEMO ($($cfg.azureConfigDir))";  User = $demo.user; Tenant = $demo.tenantId; Subscription = $demo.subscription }
)
$rows | Format-Table -AutoSize | Out-String -Width 220 | Write-Host

$checks = @(
    [pscustomobject]@{ Check = 'Demo profile folder is git-ignored'; Result = if ($ignored) { 'PASS' } else { 'FAIL' } }
    [pscustomobject]@{ Check = 'config/tenant.json is git-ignored'; Result = if ($configIgnored) { 'PASS' } else { 'FAIL' } }
    [pscustomobject]@{ Check = 'Default profile is NOT the demo tenant'; Result = if ($default -and $default.tenantId -eq $cfg.tenantId) { 'FAIL' } else { 'PASS' } }
    [pscustomobject]@{ Check = 'Demo profile is the demo tenant'; Result = if (-not $demo) { 'NOT SIGNED IN - run ./scripts/Connect-Caldova.ps1' } elseif ($demo.tenantId -eq $cfg.tenantId) { 'PASS' } else { 'FAIL' } }
)
$checks | Format-Table -AutoSize | Out-String -Width 220 | Write-Host
if ($checks.Result -contains 'FAIL') { exit 1 }
