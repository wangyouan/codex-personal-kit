param(
    [string]$CodexHome = (Join-Path $env:USERPROFILE ".codex"),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Import-Tree {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        Write-Host "Skip missing source: $Source"
        return
    }

    if ($DryRun) {
        Write-Host "[dry-run] Copy $Source -> $Destination"
        return
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force
}

Write-Host "Backing up portable Codex content from $CodexHome"

Import-Tree -Source (Join-Path $CodexHome "skills") -Destination (Join-Path $RepoRoot "skills")
Import-Tree -Source (Join-Path $CodexHome "rules") -Destination (Join-Path $RepoRoot "rules")
Import-Tree -Source (Join-Path $CodexHome "memories\global") -Destination (Join-Path $RepoRoot "memories\global")

Write-Host "Done. Review git status and git diff before committing."
