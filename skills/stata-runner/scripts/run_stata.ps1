param(
    [Parameter(Mandatory = $true)][string]$DoFile,
    [string]$StataExe
)

$ErrorActionPreference = "Stop"

function Find-StataExe {
    if ($StataExe) { return $StataExe }
    if ($env:STATA_EXE) { return $env:STATA_EXE }

    foreach ($name in @("StataMP-64.exe", "StataSE-64.exe", "StataBE-64.exe", "stata-mp.exe", "stata-se.exe")) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }

    foreach ($root in @("C:\\Program Files", "D:\\Program Files", "C:\\Stata", "D:\\Stata")) {
        if (-not (Test-Path -LiteralPath $root)) { continue }
        $candidate = Get-ChildItem -LiteralPath $root -Recurse -File -Filter "Stata*.exe" -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match "Stata(MP|SE|BE)?-?(64)?\\.exe" } |
            Select-Object -First 1
        if ($candidate) { return $candidate.FullName }
    }
    throw "Stata executable not found. Set STATA_EXE or pass -StataExe."
}

$resolvedDo = (Resolve-Path -LiteralPath $DoFile).Path
$resolvedStata = Find-StataExe
if (-not (Test-Path -LiteralPath $resolvedStata)) { throw "Stata executable not found: $resolvedStata" }

$process = Start-Process -FilePath $resolvedStata -ArgumentList @("/e", "do", $resolvedDo) -Wait -PassThru -WindowStyle Hidden
if ($process.ExitCode -ne 0) { throw "Stata exited with code $($process.ExitCode). Check the log next to the do-file." }

$logPath = [System.IO.Path]::ChangeExtension($resolvedDo, ".log")
if (Test-Path -LiteralPath $logPath) {
    $logText = Get-Content -LiteralPath $logPath -Raw
    if ($logText -match "r\\([0-9]+\\)") { throw "Stata log contains an r() error. Check: $logPath" }
}

Write-Output "Stata completed: $resolvedDo"
