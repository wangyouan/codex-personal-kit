param(
    [ValidateSet("save-credential", "test-imap", "show-config")]
    [string]$Action = "show-config",
    [string]$CredentialPath = (Join-Path $env:USERPROFILE ".codex\\xmu-mail.credential.xml")
)

$ErrorActionPreference = "Stop"

function Show-Config {
    Write-Host "XMU email client configuration"
    Write-Host "IMAP: imap.xmu.edu.cn:993 (SSL)"
    Write-Host "SMTP: smtp.xmu.edu.cn:465 (SSL)"
    Write-Host "Credential path: $CredentialPath"
}

function Save-Credential {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $CredentialPath) | Out-Null
    $credential = Get-Credential -Message "XMU email credential" -UserName "yourname@xmu.edu.cn"
    $credential | Export-Clixml -LiteralPath $CredentialPath
    Write-Host "Saved Windows-user-encrypted credential: $CredentialPath"
}

function Test-Imap {
    if (-not (Test-Path -LiteralPath $CredentialPath)) {
        throw "Credential not found. Run: xmu-mail.ps1 save-credential"
    }
    $credential = Import-Clixml -LiteralPath $CredentialPath
    $client = [System.Net.Sockets.TcpClient]::new("imap.xmu.edu.cn", 993)
    $ssl = $null
    try {
        $ssl = [System.Net.Security.SslStream]::new($client.GetStream(), $false)
        $ssl.AuthenticateAsClient("imap.xmu.edu.cn")
        $reader = [System.IO.StreamReader]::new($ssl)
        $writer = [System.IO.StreamWriter]::new($ssl)
        $writer.NewLine = "`r`n"
        $writer.AutoFlush = $true
        [void]$reader.ReadLine()
        $user = $credential.UserName.Replace("\\", "\\\\").Replace('"', '\\"')
        $password = $credential.GetNetworkCredential().Password.Replace("\\", "\\\\").Replace('"', '\\"')
        $writer.WriteLine("a001 LOGIN `"$user`" `"$password`"")
        do { $line = $reader.ReadLine() } until ($line -match "^a001\\s+(OK|NO|BAD)")
        if ($line -notmatch "^a001\\s+OK") { throw "IMAP login failed: $line" }
        $writer.WriteLine("a002 LOGOUT")
        Write-Host "IMAP login succeeded for $($credential.UserName)"
    } finally {
        if ($null -ne $ssl) { $ssl.Dispose() }
        $client.Dispose()
    }
}

switch ($Action) {
    "save-credential" { Save-Credential }
    "test-imap" { Test-Imap }
    "show-config" { Show-Config }
}
