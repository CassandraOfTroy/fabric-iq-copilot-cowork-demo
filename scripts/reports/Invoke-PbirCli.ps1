<#
.SYNOPSIS
    Runs the powerbi-report-author CLI under a repo-local portable Node.js LTS.

.DESCRIPTION
    On Windows 11 24H2, Node.js 22.x path-based stat returns dev=0 while handle-based fstat returns the
    volume serial number. The CLI's pack safety check compares both, so `pack` and `preview` fail with
    PACK_SOURCE_PATH_ESCAPE / identity_changed. Node.js 24 LTS returns consistent values.

    This wrapper downloads Node.js 24 LTS into the git-ignored .tools\ folder once (SHA-256 verified
    against nodejs.org SHASUMS256.txt) and runs the globally installed CLI with it. The global Node.js
    installation is never changed.

.EXAMPLE
    .\scripts\reports\Invoke-PbirCli.ps1 validate "fabric\Supplier Invoice Assurance.Report"
#>
# No param block / CmdletBinding on purpose: every argument (including --out, which would collide with the
# -OutVariable/-OutBuffer common parameters) is forwarded verbatim through $args.
$CliArgs = @($args)

$ErrorActionPreference = 'Stop'
$NodeVersion = 'v24.21.0'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
# Preview/publish authenticate through the Azure CLI: always use this repo's demo-tenant profile, never the default login
. (Join-Path $RepoRoot 'scripts\Use-CaldovaTenant.ps1') *> $null
$ToolsDir = Join-Path $RepoRoot '.tools'
$NodeName = "node-$NodeVersion-win-x64"
$NodeExe = Join-Path $ToolsDir "$NodeName\node.exe"

if (-not (Test-Path $NodeExe)) {
    New-Item -ItemType Directory -Path $ToolsDir -Force | Out-Null
    $zip = Join-Path $ToolsDir "$NodeName.zip"
    Write-Host "[pbir] Downloading portable Node.js $NodeVersion to $ToolsDir ..."
    Invoke-WebRequest -Uri "https://nodejs.org/dist/$NodeVersion/$NodeName.zip" -OutFile $zip -TimeoutSec 600
    $sums = (Invoke-WebRequest -Uri "https://nodejs.org/dist/$NodeVersion/SHASUMS256.txt" -TimeoutSec 60).Content
    $expected = (($sums -split "`n") | Where-Object { $_ -match "  $([regex]::Escape($NodeName)).zip$" }) -replace '\s+.*$', ''
    $actual = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
    if (-not $expected -or $expected -ne $actual) {
        Remove-Item $zip -Force -ErrorAction SilentlyContinue
        throw "Node.js download hash mismatch (expected '$expected', got '$actual')."
    }
    Expand-Archive -Path $zip -DestinationPath $ToolsDir -Force
    Remove-Item $zip -Force
}

$npmRoot = (& npm root -g).Trim()
$cliJs = Join-Path $npmRoot '@microsoft\powerbi-report-authoring-cli\dist\cli.js'
if (-not (Test-Path $cliJs)) {
    throw "powerbi-report-author CLI not found at $cliJs. Install it globally first (npm install -g @microsoft/powerbi-report-authoring-cli)."
}

& $NodeExe $cliJs @CliArgs
exit $LASTEXITCODE
