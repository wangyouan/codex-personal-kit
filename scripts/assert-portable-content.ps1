param(
    [Parameter(Mandatory = $true)][string[]]$Path
)

$ErrorActionPreference = "Stop"

$blockedNamePattern = '(?i)(^|[._-])(auth|credential|secret|token)([._-]|$)|\.env$|\.sqlite($|[-.])|\.db$'
$blockedContentPatterns = @(
    '(?i)^\s*(JOPLIN_TOKEN|XMU_MAIL_PASSWORD|OPENAI_API_KEY|ANTHROPIC_API_KEY)\s*=',
    '(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    '(?i)\b[A-Z]:\\Users\\'
)

foreach ($root in $Path) {
    if (-not (Test-Path -LiteralPath $root)) { continue }
    foreach ($file in Get-ChildItem -LiteralPath $root -Recurse -File -Force) {
        $relative = $file.FullName.Substring($root.Length).TrimStart([char[]]@('\', '/'))
        if ($relative -match '(?i)(^|[\\/])(cache|sessions?|attachments|plugins[\\/]cache)([\\/]|$)') {
            throw "Non-portable runtime directory detected: $($file.FullName)"
        }
        if ($file.Name -match $blockedNamePattern) {
            throw "Non-portable file name detected: $($file.FullName)"
        }
        if ($file.Length -gt 5MB) { continue }
        foreach ($pattern in $blockedContentPatterns) {
            if (Select-String -LiteralPath $file.FullName -Pattern $pattern -Quiet) {
                throw "Non-portable content detected: $($file.FullName)"
            }
        }
    }
}

Write-Output "Portable-content check passed for $($Path.Count) path(s)."
