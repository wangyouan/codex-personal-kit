param(
    [string]$CodexHome = (Join-Path $env:USERPROFILE ".codex"),
    [switch]$Apply,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
. (Join-Path $PSScriptRoot "manifest.ps1")

if ($Apply -and $DryRun) { throw "Use either -Apply or -DryRun, not both." }
$isApply = $Apply -and -not $DryRun
$manifest = Get-PersonalKitManifest -Path (Join-Path $RepoRoot "skills-manifest.toml")
$portableCheck = Join-Path $PSScriptRoot "assert-portable-content.ps1"

function Export-Tree {
    param([string]$Source, [string]$Destination, [string]$Label)
    if (-not (Test-Path -LiteralPath $Source)) { Write-Host "[missing] $Label"; return }
    Write-Host "[export] ${Label}: $Source -> $Destination"
    if (-not $isApply) { return }
    & $portableCheck -Path $Source
    if ($LASTEXITCODE -ne 0) { throw "Portable-content check failed: $Label" }
    if (Test-Path -LiteralPath $Destination) { Remove-Item -LiteralPath $Destination -Recurse -Force }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
}

if ($isApply) {
    Write-Host "Export mode: apply"
} else {
    Write-Host "Export mode: preview (pass -Apply to write)"
}
foreach ($entry in $manifest | Where-Object { $_.mode -eq "vendor" -and $_.exportable }) {
    Export-Tree -Source (Join-Path (Join-Path $CodexHome "skills") $entry.install_name) -Destination (Join-Path $RepoRoot $entry.source_path) -Label $entry.name
}
Export-Tree -Source (Join-Path $CodexHome "rules") -Destination (Join-Path $RepoRoot "rules") -Label "rules"
Export-Tree -Source (Join-Path $CodexHome "memories\\global") -Destination (Join-Path $RepoRoot "memories\\global") -Label "memories/global"
