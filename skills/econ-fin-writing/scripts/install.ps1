[CmdletBinding()]
param(
    [ValidateSet("Codex", "Claude", "Both")]
    [string]$Target = "Both",
    [string]$CodexSkillsRoot = (Join-Path $env:USERPROFILE ".agents\skills"),
    [string]$LegacyCodexSkillsRoot = (Join-Path $env:USERPROFILE ".codex\skills"),
    [string]$ClaudeSkillsRoot = (Join-Path $env:USERPROFILE ".claude\skills"),
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$skillName = "econ-fin-writing"

function Install-Skill {
    param([string]$SkillsRoot)

    $destination = Join-Path $SkillsRoot $skillName
    if ($DryRun) {
        Write-Host "[dry-run] Copy $repoRoot -> $destination"
        return
    }

    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    Get-ChildItem -LiteralPath $repoRoot -Force | Where-Object {
        $_.Name -ne ".git"
    } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $destination $_.Name) -Recurse -Force
    }
    Write-Host "Installed $skillName into $destination"
}

if ($Target -in @("Codex", "Both")) {
    @($CodexSkillsRoot, $LegacyCodexSkillsRoot) | Select-Object -Unique | ForEach-Object {
        Install-Skill -SkillsRoot $_
    }
}

if ($Target -in @("Claude", "Both")) {
    Install-Skill -SkillsRoot $ClaudeSkillsRoot
}
