param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$Args
)

$root = Split-Path -Parent $PSScriptRoot
$stateDir = Join-Path $root "state"
$logFile = Join-Path $stateDir "notify-events.jsonl"

New-Item -ItemType Directory -Force $stateDir | Out-Null

$payload = [ordered]@{
  ts = (Get-Date).ToString("s")
  raw = ($Args -join " ")
}

$line = $payload | ConvertTo-Json -Compress -Depth 6
Add-Content -Path $logFile -Value $line -Encoding utf8
