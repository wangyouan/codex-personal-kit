param(
    [string]$CodexHome = (Join-Path $env:USERPROFILE ".codex")
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "Repository: $RepoRoot"
Write-Host "Codex home: $CodexHome"
Write-Host ""

foreach ($Name in @("skills", "rules", "memories\global", "memories\local")) {
    $Path = Join-Path $CodexHome $Name
    if (Test-Path -LiteralPath $Path) {
        $Count = (Get-ChildItem -LiteralPath $Path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Host "$Name : $Count files"
    } else {
        Write-Host "$Name : missing"
    }
}
