param(
    [string]$CodexHome = (Join-Path $env:USERPROFILE ".codex"),
    [switch]$Apply,
    [switch]$DryRun,
    [switch]$SkipExternal,
    [switch]$RefreshExternal,
    [string[]]$SkillName
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
. (Join-Path $PSScriptRoot "manifest.ps1")

if ($Apply -and $DryRun) { throw "Use either -Apply or -DryRun, not both." }
if ($RefreshExternal -and -not $Apply) { throw "-RefreshExternal requires -Apply." }
$isApply = $Apply -and -not $DryRun
$manifest = Get-PersonalKitManifest -Path (Join-Path $RepoRoot "skills-manifest.toml")
if ($SkillName) {
    $unknown = $SkillName | Where-Object { $_ -notin $manifest.name }
    if ($unknown) { throw "Unknown skill name(s): $($unknown -join ', ')" }
    $manifest = $manifest | Where-Object { $_.name -in $SkillName }
}
$backupRoot = Join-Path $CodexHome ("backups\\personal-kit\\" + (Get-Date -Format "yyyyMMdd-HHmmss"))

function Backup-Target {
    param([string]$Target)
    if (-not (Test-Path -LiteralPath $Target)) { return }
    $name = Split-Path -Leaf $Target
    $backup = Join-Path $backupRoot $name
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    Copy-Item -LiteralPath $Target -Destination $backup -Recurse -Force
    Write-Host "  backed up existing skill to $backup"
}

function Sync-VendorSkill {
    param($Entry)
    $source = Join-Path $RepoRoot $Entry.source_path
    $target = Join-Path (Join-Path $CodexHome "skills") $Entry.install_name
    if (-not (Test-Path -LiteralPath $source)) { throw "Vendor source missing: $source" }
    $sourceHash = Get-PersonalKitTreeHash -Path $source
    $targetHash = Get-PersonalKitTreeHash -Path $target
    if ($sourceHash -eq $targetHash) {
        Write-Host "[unchanged] $($Entry.name)"
        return
    }
    $verb = if ($null -eq $targetHash) { "install" } else { "update" }
    Write-Host "[$verb] $($Entry.name) -> $target"
    if (-not $isApply) { return }
    if (Test-Path -LiteralPath $target) {
        Backup-Target -Target $target
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
}

function Install-ExternalSkill {
    param($Entry)
    $target = Join-Path (Join-Path $CodexHome "skills") $Entry.install_name
    if ((Test-Path -LiteralPath $target) -and -not $RefreshExternal) {
        Write-Host "[present] $($Entry.name) (use -Apply -RefreshExternal to reinstall its pinned ref)"
        return
    }
    Write-Host "[external] $($Entry.name) from $($Entry.source_repo)@$($Entry.source_ref)"
    if (-not $isApply -or $SkipExternal) { return }
    if (Test-Path -LiteralPath $target) {
        Backup-Target -Target $target
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    $git = Get-Command git -ErrorAction Stop
    $temporaryRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("personal-kit-" + [guid]::NewGuid().ToString("N"))
    $checkout = Join-Path $temporaryRoot "repo"
    try {
        New-Item -ItemType Directory -Force -Path $temporaryRoot | Out-Null
        & $git.Source clone --filter=blob:none --no-checkout ("https://github.com/" + $Entry.source_repo + ".git") $checkout
        if ($LASTEXITCODE -ne 0) { throw "Could not clone $($Entry.source_repo)" }
        & $git.Source -C $checkout fetch --depth 1 origin $Entry.source_ref
        if ($LASTEXITCODE -ne 0) { throw "Could not fetch pinned ref $($Entry.source_ref) for $($Entry.name)" }
        & $git.Source -C $checkout checkout --detach FETCH_HEAD
        if ($LASTEXITCODE -ne 0) { throw "Could not check out pinned ref for $($Entry.name)" }
        $source = Join-Path $checkout $Entry.source_path
        if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md"))) { throw "Pinned source does not contain SKILL.md: $source" }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
        Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
    } finally {
        if (Test-Path -LiteralPath $temporaryRoot) { Remove-Item -LiteralPath $temporaryRoot -Recurse -Force }
    }
}

Write-Host "Codex Personal Kit: $RepoRoot"
if ($isApply) {
    Write-Host "Mode: apply"
    New-Item -ItemType Directory -Force -Path (Join-Path $CodexHome "skills") | Out-Null
} else {
    Write-Host "Mode: preview (pass -Apply to write)"
}

foreach ($entry in $manifest | Where-Object mode -eq "vendor") { Sync-VendorSkill -Entry $entry }
foreach ($entry in $manifest | Where-Object mode -eq "external") { Install-ExternalSkill -Entry $entry }
foreach ($entry in $manifest | Where-Object mode -eq "archive") { Write-Host "[archive] $($entry.name) is not installed" }

foreach ($relativePath in @("rules", "memories\\global")) {
    $source = Join-Path $RepoRoot $relativePath
    $target = Join-Path $CodexHome $relativePath
    Write-Host "[sync] $relativePath -> $target"
    if ($isApply -and (Test-Path -LiteralPath $source)) {
        New-Item -ItemType Directory -Force -Path $target | Out-Null
        Copy-Item -Path (Join-Path $source "*") -Destination $target -Recurse -Force
    }
}

if ($isApply) { New-Item -ItemType Directory -Force -Path (Join-Path $CodexHome "memories\\local") | Out-Null }
Write-Host "Post-install reminders:"
foreach ($entry in $manifest | Where-Object { $_.post_install -and $_.post_install -ne "none" }) { Write-Host "- $($entry.name): $($entry.post_install)" }
