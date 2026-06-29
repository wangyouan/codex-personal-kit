param(
    [string]$CodexHome = (Join-Path $env:USERPROFILE ".codex"),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Copy-Tree {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return
    }

    if ($DryRun) {
        Write-Host "[dry-run] Copy $Source -> $Destination"
        return
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force
}

Write-Host "Installing Codex Personal Kit into $CodexHome"

if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $CodexHome | Out-Null
}

Copy-Tree -Source (Join-Path $RepoRoot "skills") -Destination (Join-Path $CodexHome "skills")
Copy-Tree -Source (Join-Path $RepoRoot "rules") -Destination (Join-Path $CodexHome "rules")
Copy-Tree -Source (Join-Path $RepoRoot "memories\global") -Destination (Join-Path $CodexHome "memories\global")

$LocalMemory = Join-Path $CodexHome "memories\local"
if ($DryRun) {
    Write-Host "[dry-run] Ensure local memory folder exists: $LocalMemory"
} else {
    New-Item -ItemType Directory -Force -Path $LocalMemory | Out-Null
}

Write-Host "Done."
