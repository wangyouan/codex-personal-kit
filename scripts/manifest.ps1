function Get-PersonalKitManifest {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Manifest not found: $Path"
    }

    $entries = @()
    $current = $null
    foreach ($rawLine in Get-Content -LiteralPath $Path) {
        $line = $rawLine.Trim()
        if (-not $line -or $line.StartsWith("#")) { continue }
        if ($line -eq "[[skill]]") {
            if ($null -ne $current) { $entries += [PSCustomObject]$current }
            $current = @{}
            continue
        }
        if ($null -eq $current) { continue }
        if ($line -match '^(?<key>[A-Za-z_]+)\s*=\s*"(?<value>.*)"\s*$') {
            $current[$Matches.key] = $Matches.value
            continue
        }
        if ($line -match '^(?<key>[A-Za-z_]+)\s*=\s*(?<value>true|false)\s*$') {
            $current[$Matches.key] = [System.Convert]::ToBoolean($Matches.value)
            continue
        }
        throw "Unsupported manifest line: $rawLine"
    }
    if ($null -ne $current) { $entries += [PSCustomObject]$current }
    return $entries
}

function Get-PersonalKitTreeHash {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $lines = foreach ($file in Get-ChildItem -LiteralPath $Path -Recurse -File | Sort-Object FullName) {
        $relative = $file.FullName.Substring($Path.Length).TrimStart([char[]]@('\', '/'))
        "$relative|$($file.Length)|$((Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash)"
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes(($lines -join "`n"))
    return ([System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
}
