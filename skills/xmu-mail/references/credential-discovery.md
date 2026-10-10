# Credential Discovery

Use this when another task cannot find existing XMU mail credentials. Inspect only the named environment variables and optional credential file; never dump their contents.

## Discovery Order

1. Inspect Process `XMU_MAIL_USER` and `XMU_MAIL_PASSWORD` for non-empty values. The Python helper reads these; `--user` overrides the username only.
2. If incomplete, inspect User environment under the actual invoking Windows user, using the authorized execution context when required. Machine environment is an optional fallback only if configured. A sandbox may inherit Process variables while its own User scope is empty.
3. If still incomplete, check `$HOME/.codex/xmu-mail.credential.xml`. Import it only in the same Windows user/machine context that created it. Do not display the XML, PSCredential, SecureString, password, or registry values.
4. If no supported source is available, explain what is missing and let the user configure it locally. Do not scan shell history, agent logs, arbitrary configuration files, or browser stores for passwords.

On 2026OfficePC, verified 2026-10-10: Process and the authorized user's User scope contained both variables; Machine scope did not; the optional XML file was absent. IMAP read access succeeded. This is a dated device observation, not a guarantee about another task or ThinkBook.

## Safe Presence Check

Use the latest installed `pwsh`. The following emits booleans only:

```powershell
foreach ($scope in @('Process', 'User', 'Machine')) {
    [pscustomobject]@{
        Scope = $scope
        UserPresent = -not [string]::IsNullOrWhiteSpace(
            [Environment]::GetEnvironmentVariable('XMU_MAIL_USER', $scope))
        PasswordPresent = -not [string]::IsNullOrWhiteSpace(
            [Environment]::GetEnvironmentVariable('XMU_MAIL_PASSWORD', $scope))
    }
}
Test-Path -LiteralPath (Join-Path $HOME '.codex/xmu-mail.credential.xml')
```

Do not use `Get-ChildItem Env:`, `Get-Content` on credential files, `Get-ItemProperty` dumps, or `Write-Output $env:XMU_MAIL_PASSWORD` for diagnostics. User environment variables are persistent configuration, not an encrypted credential vault.

## Temporary Loading and Read-Only Test

Run this in the authorized user's context. Set `$mailScript` to the actual installed helper location if it differs. Existing Process values win; only missing variables are loaded. DPAPI is optional. The environment is restored after the child command.

```powershell
$mailScript = Join-Path $HOME '.codex/skills/xmu-mail/scripts/xmu_mail.py'
$oldUser = $env:XMU_MAIL_USER
$oldPassword = $env:XMU_MAIL_PASSWORD
try {
    foreach ($name in @('XMU_MAIL_USER', 'XMU_MAIL_PASSWORD')) {
        if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, 'Process'))) {
            foreach ($scope in @('User', 'Machine')) {
                $value = [Environment]::GetEnvironmentVariable($name, $scope)
                if (-not [string]::IsNullOrWhiteSpace($value)) {
                    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
                    break
                }
            }
        }
    }
    if ([string]::IsNullOrWhiteSpace($env:XMU_MAIL_USER) -or
        [string]::IsNullOrWhiteSpace($env:XMU_MAIL_PASSWORD)) {
        $credentialPath = Join-Path $HOME '.codex/xmu-mail.credential.xml'
        if (Test-Path -LiteralPath $credentialPath) {
            $credential = Import-Clixml -LiteralPath $credentialPath
            if ($credential -isnot [System.Management.Automation.PSCredential]) {
                throw 'Unexpected credential file type.'
            }
            if (-not [string]::IsNullOrWhiteSpace($env:XMU_MAIL_USER) -and
                $env:XMU_MAIL_USER -ne $credential.UserName) {
                throw 'Credential account mismatch; do not combine different accounts.'
            }
            if ([string]::IsNullOrWhiteSpace($env:XMU_MAIL_USER)) {
                $env:XMU_MAIL_USER = $credential.UserName
            }
            if ([string]::IsNullOrWhiteSpace($env:XMU_MAIL_PASSWORD)) {
                $env:XMU_MAIL_PASSWORD = $credential.GetNetworkCredential().Password
            }
        }
    }
    if ([string]::IsNullOrWhiteSpace($env:XMU_MAIL_USER) -or
        [string]::IsNullOrWhiteSpace($env:XMU_MAIL_PASSWORD)) {
        throw 'Existing XMU credentials are unavailable in this execution context.'
    }
    $env:PYTHONIOENCODING = 'utf-8'
    python $mailScript folders
    if ($LASTEXITCODE -ne 0) { throw 'Read-only IMAP test failed; check the reported failure category.' }
} finally {
    $env:XMU_MAIL_USER = $oldUser
    $env:XMU_MAIL_PASSWORD = $oldPassword
    $credential = $null
    $value = $null
}
```

`folders` lists folder names, not passwords or message bodies. Subsequent `search` and `read` commands use read-only IMAP selection and `BODY.PEEK`; they do not mark messages read. Never include password literals in a command, file, chat, or process argument.

For Sent Items, preserve IMAP quoting in PowerShell:

```powershell
python $mailScript search --folder '"Sent Items"' --query ALL --limit 3
```

## Failure Boundaries

- Missing file alone: continue checking the supported environment sources.
- Socket permission denied: ask for the required execution/network permission; do not rotate credentials, retry indefinitely, or disable TLS.
- IMAP authentication rejected: stop repeated login attempts and report the category without exposing credentials.
- DPAPI cannot decrypt: use the original Windows user/machine or locally reconfigure; never copy the encrypted file and assume it is portable.
- Credentials changed outside the task: restart the app or temporarily load the updated User environment; an already-running app may retain old Process values.
- A different mailbox: do not reuse XMU credentials or claim access. User screenshots can substantiate a deadline without mailbox login.

