param(
    [Parameter(Mandatory = $true)][string[]]$NoteId,
    [string]$BaseUrl = "http://127.0.0.1:41184",
    [string]$Token = $env:JOPLIN_TOKEN,
    [switch]$Apply
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Net.Http
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$documentBody = [string](Get-Content -LiteralPath (Join-Path $RepoRoot "docs\\skill-inventory.md") -Raw)

if (-not $Apply) {
    foreach ($id in $NoteId) { Write-Host "[preview] Would update Joplin note $id from docs/skill-inventory.md" }
    return
}
if (-not $Token) { throw "Set JOPLIN_TOKEN locally before updating Joplin." }

$client = [System.Net.Http.HttpClient]::new()
try {
    foreach ($id in $NoteId) {
        $uri = "${BaseUrl}/notes/${id}?token=${Token}"
        $payload = @{ body = $documentBody } | ConvertTo-Json -Compress
        $content = [System.Net.Http.StringContent]::new($payload, [System.Text.Encoding]::UTF8, "application/json")
        $response = $client.PutAsync($uri, $content).GetAwaiter().GetResult()
        if (-not $response.IsSuccessStatusCode) {
            $detail = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
            throw "Joplin update failed for $id ($([int]$response.StatusCode)): $detail"
        }
        Write-Host "Updated Joplin note $id"
    }
} finally {
    $client.Dispose()
}
