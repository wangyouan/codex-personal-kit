$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot '../../stata-regression-workflow/scripts/test_runner.ps1')

# Exercise the real compatibility wrapper against an isolated stand-in runner.
$temporaryRoot = Join-Path ([IO.Path]::GetTempPath()) ('stata-alias-test-' + [guid]::NewGuid().ToString('N'))
$wrapperDirectory = Join-Path $temporaryRoot 'skills/stata-runner/scripts'
$runnerDirectory = Join-Path $temporaryRoot 'skills/stata-regression-workflow/scripts'
try {
    New-Item -ItemType Directory -Path $wrapperDirectory,$runnerDirectory -Force | Out-Null
    $wrapper = Join-Path $wrapperDirectory 'run_stata.ps1'
    $runner = Join-Path $runnerDirectory 'run_stata.ps1'
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'run_stata.ps1') -Destination $wrapper
    $standIn = @'
param([Parameter(Mandatory = $true)][string]$DoFile, [string]$StataExe)
[pscustomobject]@{ DoFile = $DoFile; StataExe = $StataExe }
'@
    [IO.File]::WriteAllText($runner, $standIn)
    $doFile = Join-Path $temporaryRoot 'project with spaces/analysis.do'
    $executable = Join-Path $temporaryRoot 'Stata with spaces/StataMP-64.exe'
    $result = & $wrapper -DoFile $doFile -StataExe $executable
    if ($result.DoFile -ne $doFile -or $result.StataExe -ne $executable) {
        throw 'Compatibility runner did not preserve explicit parameters.'
    }
    $result = & $wrapper -DoFile $doFile
    if ($result.DoFile -ne $doFile -or $result.StataExe) {
        throw 'Compatibility runner changed omitted optional parameters.'
    }
    Remove-Item -LiteralPath $runner
    $rejected = $false
    try { & $wrapper -DoFile $doFile | Out-Null }
    catch {
        if ($_.Exception.Message -notlike '*Install stata-regression-workflow*') { throw }
        $rejected = $true
    }
    if (-not $rejected) { throw 'Missing canonical runner was not rejected.' }
    'Compatibility forwarding checks passed.'
} finally {
    $resolvedRoot = [IO.Path]::GetFullPath($temporaryRoot)
    $tempParent = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([char[]]@('\','/')) + [IO.Path]::DirectorySeparatorChar
    if (-not $resolvedRoot.StartsWith($tempParent, [StringComparison]::OrdinalIgnoreCase) -or
        (Split-Path $resolvedRoot -Leaf) -notlike 'stata-alias-test-*') {
        throw 'Refusing cleanup outside the intended temporary test directory.'
    }
    if (Test-Path -LiteralPath $resolvedRoot) { Remove-Item -LiteralPath $resolvedRoot -Recurse -Force }
}
