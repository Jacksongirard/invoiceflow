# InvoiceFlow local server for Windows (no Python required)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$SyncFile = Join-Path $Root 'invoiceflow-data.json'
$LegacyFile = Join-Path $Root 'data.json'
if (Test-Path -LiteralPath $SyncFile) { $DataFile = $SyncFile } elseif (Test-Path -LiteralPath $LegacyFile) { $DataFile = $LegacyFile } else { $DataFile = $SyncFile }
$IndexFile = Join-Path $Root 'index.html'
$HostName = '127.0.0.1'
$Port = 8765

Write-Host ""
Write-Host "  InvoiceFlow server"
Write-Host "  =================="
Write-Host "  Folder: $Root"
Write-Host "  index.html present: $(Test-Path -LiteralPath $IndexFile)"
Write-Host ""

if (-not (Test-Path -LiteralPath $IndexFile)) {
  Write-Host "  ERROR: index.html is missing."
  Write-Host "  Wait for Dropbox to finish syncing the app folder, then try again."
  Write-Host ""
  Read-Host "Press Enter to close"
  exit 1
}

if (-not (Test-Path -LiteralPath $DataFile)) {
  Set-Content -Path $DataFile -Value "{}" -Encoding UTF8
}

$listener = $null
$Prefix = $null
foreach ($tryPrefix in @("http://127.0.0.1:8765/", "http://localhost:8765/")) {
  try {
    $candidate = New-Object System.Net.HttpListener
    $candidate.Prefixes.Add($tryPrefix)
    $candidate.Start()
    $listener = $candidate
    $Prefix = $tryPrefix
    break
  } catch {
    if ($null -ne $candidate) { try { $candidate.Close() } catch {} }
  }
}

if ($null -eq $listener) {
  Write-Host "  Could not start on port 8765."
  Write-Host "  Close any other InvoiceFlow window and try again."
  Write-Host ""
  Read-Host "Press Enter to close"
  exit 1
}

Write-Host "  Open: $($Prefix)index.html"
Write-Host "  Data: $DataFile"
Write-Host "  Leave this window open. Press Ctrl+C when finished."
Write-Host ""

Start-Process ($Prefix + 'index.html') | Out-Null

function Get-ContentType([string]$path) {
  switch -Regex ([IO.Path]::GetExtension($path).ToLowerInvariant()) {
    '\.html?' { return 'text/html; charset=utf-8' }
    '\.js'    { return 'application/javascript; charset=utf-8' }
    '\.css'   { return 'text/css; charset=utf-8' }
    '\.json'  { return 'application/json; charset=utf-8' }
    default   { return 'application/octet-stream' }
  }
}

function Send-Bytes($ctx, [int]$code, [string]$contentType, [byte[]]$bytes) {
  $ctx.Response.StatusCode = $code
  $ctx.Response.ContentType = $contentType
  $ctx.Response.Headers['Cache-Control'] = 'no-store'
  $ctx.Response.Headers['Access-Control-Allow-Origin'] = '*'
  $ctx.Response.ContentLength64 = $bytes.Length
  $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  $ctx.Response.OutputStream.Close()
}

function Send-Json($ctx, [int]$code, $obj) {
  $json = $obj | ConvertTo-Json -Depth 100 -Compress
  $bytes = [Text.Encoding]::UTF8.GetBytes($json)
  Send-Bytes $ctx $code 'application/json; charset=utf-8' $bytes
}

function Send-Text($ctx, [int]$code, [string]$text, [string]$contentType) {
  $bytes = [Text.Encoding]::UTF8.GetBytes($text)
  Send-Bytes $ctx $code $contentType $bytes
}

try {
  while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $req = $ctx.Request
    $path = $req.Url.AbsolutePath

    try {
      if ($req.HttpMethod -eq 'OPTIONS') {
        $ctx.Response.StatusCode = 204
        $ctx.Response.Headers['Access-Control-Allow-Origin'] = '*'
        $ctx.Response.Headers['Access-Control-Allow-Methods'] = 'GET, PUT, OPTIONS'
        $ctx.Response.Headers['Access-Control-Allow-Headers'] = 'Content-Type'
        $ctx.Response.Close()
        continue
      }

      if ($path -eq '/api/status') {
        Send-Json $ctx 200 @{
          ok = $true
          mode = 'file'
          root = $Root
          indexExists = (Test-Path -LiteralPath $IndexFile)
          dataFile = $DataFile
          exists = (Test-Path -LiteralPath $DataFile)
        }
        continue
      }

      if ($path -eq '/api/data') {
        if ($req.HttpMethod -eq 'GET') {
          if (Test-Path -LiteralPath $DataFile) {
            $raw = Get-Content -LiteralPath $DataFile -Raw -Encoding UTF8
            if ([string]::IsNullOrWhiteSpace($raw)) { $raw = '{}' }
            $data = $raw | ConvertFrom-Json
            Send-Json $ctx 200 @{ ok = $true; data = $data; path = $DataFile }
          } else {
            Send-Json $ctx 200 @{ ok = $true; data = $null; path = $DataFile }
          }
          continue
        }
        if ($req.HttpMethod -eq 'PUT') {
          $reader = New-Object IO.StreamReader($req.InputStream, $req.ContentEncoding)
          $body = $reader.ReadToEnd()
          $reader.Close()
          $payload = $body | ConvertFrom-Json
          $toSave = $payload
          if ($null -ne $payload.data) { $toSave = $payload.data }
          $jsonOut = $toSave | ConvertTo-Json -Depth 100
          $tmp = "$DataFile.tmp"
          Set-Content -LiteralPath $tmp -Value $jsonOut -Encoding UTF8
          Move-Item -LiteralPath $tmp -Destination $DataFile -Force
          Send-Json $ctx 200 @{ ok = $true; path = $DataFile }
          continue
        }
        Send-Json $ctx 405 @{ ok = $false; error = 'Method not allowed' }
        continue
      }

      # App pages
      if ($path -eq '/' -or $path -eq '' -or $path -eq '/index.html' -or $path -eq '/index.htm') {
        if (-not (Test-Path -LiteralPath $IndexFile)) {
          Send-Text $ctx 404 "<h1>index.html missing</h1><p>Wait for Dropbox sync.</p>" 'text/html; charset=utf-8'
          continue
        }
        $bytes = [IO.File]::ReadAllBytes($IndexFile)
        Send-Bytes $ctx 200 'text/html; charset=utf-8' $bytes
        continue
      }

      $rel = $path.TrimStart('/')
      $rel = $rel -replace '/', [IO.Path]::DirectorySeparatorChar
      $filePath = [IO.Path]::GetFullPath((Join-Path $Root $rel))
      if (-not $filePath.StartsWith($Root, [StringComparison]::OrdinalIgnoreCase)) {
        Send-Text $ctx 403 'Forbidden' 'text/plain'
        continue
      }
      if (-not (Test-Path -LiteralPath $filePath) -or (Get-Item -LiteralPath $filePath).PSIsContainer) {
        Send-Text $ctx 404 'Not found' 'text/plain'
        continue
      }
      $bytes = [IO.File]::ReadAllBytes($filePath)
      Send-Bytes $ctx 200 (Get-ContentType $filePath) $bytes
    } catch {
      try { Send-Json $ctx 500 @{ ok = $false; error = $_.Exception.Message } } catch {}
    }
  }
} finally {
  try { $listener.Stop() } catch {}
  try { $listener.Close() } catch {}
}
