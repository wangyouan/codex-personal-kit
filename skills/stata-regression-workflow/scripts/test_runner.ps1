$ErrorActionPreference = 'Stop'
$tokens = $null
$parseErrors = $null
$path = Join-Path $PSScriptRoot 'run_stata.ps1'
$ast = [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'Runner syntax errors' }
$patterns = @($ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.BinaryExpressionAst] -and $node.Operator -eq 'Imatch' }, $true))
$namePattern = ($patterns | Where-Object { $_.Left.Extent.Text -eq '$_.Name' }).Right.Value
$errorPattern = ($patterns | Where-Object { $_.Left.Extent.Text -eq '$logText' }).Right.Value
foreach ($name in 'StataMP-64.exe','StataSE-64.exe','StataBE-64.exe','Stata.exe') {
    if ($name -notmatch $namePattern) { throw "Executable rejected: $name" }
}
foreach ($name in 'StataMP-64_old.exe','StataMP-64.exe.bak') {
    if ($name -match $namePattern) { throw "Backup executable accepted: $name" }
}
if ("r(199);`r`n" -notmatch $errorPattern) { throw 'Error not detected' }
if ('. display "r(199);"' -match $errorPattern) { throw 'Source text treated as an error' }
'Runner regression checks passed.'
