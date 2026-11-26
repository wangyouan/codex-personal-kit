param(
    [Parameter(Mandatory = $true)][string]$DoFile,
    [string]$StataExe
)
$ErrorActionPreference = 'Stop'
$target = Join-Path $PSScriptRoot '../../stata-regression-workflow/scripts/run_stata.ps1'
if (-not (Test-Path -LiteralPath $target)) { throw 'Install stata-regression-workflow before using this compatibility runner.' }
& $target @PSBoundParameters
