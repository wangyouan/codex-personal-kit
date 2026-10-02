param([switch]$Apply, [string]$Version = '4.6.1')
$ErrorActionPreference = 'Stop'
if ($Version -notmatch '^\d+\.\d+\.\d+$') { throw 'Invalid R version' }
$base = 'https://cran.r-project.org/bin/windows/base/'
$file = "R-$Version-win.exe"
$target = Join-Path $env:LOCALAPPDATA "Programs\R\R-$Version"
Write-Output "Official CRAN installer: $base$file"
Write-Output "Current-user installation: $target"
if (-not $Apply) { Write-Output 'Preview only. Use -Apply to install R and research packages.'; return }
$installer = Join-Path $env:TEMP $file
if (-not (Test-Path -LiteralPath $installer)) { Invoke-WebRequest ($base + $file) -OutFile $installer }
$checks = (Invoke-WebRequest ($base + "md5sum.R-$Version.txt")).Content
$hash = (Get-FileHash -LiteralPath $installer -Algorithm MD5).Hash
$line = $checks -split "`n" | Where-Object { $_ -match [regex]::Escape($file) }
if (-not $line -or $line -notmatch $hash) { throw 'Official checksum mismatch' }
$sig = Get-AuthenticodeSignature -LiteralPath $installer
if ($sig.Status -ne 'Valid') { throw "Installer signature is $($sig.Status)" }
$proc = Start-Process -FilePath $installer -ArgumentList @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/CURRENTUSER', "/DIR=`"$target`"", '/TASKS=') -WindowStyle Hidden -Wait -PassThru
if ($proc.ExitCode -ne 0) { throw "R installer exited $($proc.ExitCode)" }
$rscript = Join-Path $target 'bin\Rscript.exe'
if (-not (Test-Path -LiteralPath $rscript)) { throw 'Rscript missing after installation' }
[Environment]::SetEnvironmentVariable('RSCRIPT_EXE', $rscript, 'User')
$env:RSCRIPT_EXE = $rscript
$oldLocale = $env:LC_ALL
try {
    $env:LC_ALL = 'English_United States.utf8'
    & $rscript --vanilla (Join-Path $PSScriptRoot 'install-r-research-packages.R')
    if ($LASTEXITCODE -ne 0) { throw 'Research package setup failed' }
} finally { $env:LC_ALL = $oldLocale }
