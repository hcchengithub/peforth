[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Message,

    [string]$MessageFile,

    [string]$Token = $env:LINE_CHANNEL_ACCESS_TOKEN,

    [string]$UserId = $env:LINE_USER_ID,

    [string]$Endpoint = $env:LINE_API_ENDPOINT,

    [switch]$Disabled = ($env:LINE_NOTIFY_DISABLED -eq '1')
)

if (-not $Endpoint) {
    $Endpoint = "https://api.line.me/v2/bot/message/push"
}

if ($MessageFile) {
    if (-not (Test-Path $MessageFile)) {
        throw "Message file not found: $MessageFile"
    }
    $Message = Get-Content $MessageFile -Raw -Encoding UTF8
}

if ([string]::IsNullOrWhiteSpace($Message)) {
    throw "Message text is required."
}

if ([string]::IsNullOrWhiteSpace($Token)) {
    throw "LINE_CHANNEL_ACCESS_TOKEN is required (set environment variable or pass -Token)."
}

if ([string]::IsNullOrWhiteSpace($UserId)) {
    throw "LINE_USER_ID is required (set environment variable or pass -UserId)."
}

$payloadObj = @{
    to = $UserId
    messages = @(
        @{
            type = "text"
            text = $Message
        }
    )
}
$jsonPayload = $payloadObj | ConvertTo-Json -Depth 5 -Compress

if ($Disabled) {
    Write-Output "LINE_NOTIFY_DISABLED=1: Payload prepared but not sent."
    Write-Output $jsonPayload
    return
}

$headers = @{
    Authorization = "Bearer $Token"
}

$response = Invoke-WebRequest -Uri $Endpoint -Method Post -Headers $headers -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload))

if ($response.StatusCode -eq 200) {
    Write-Output "LINE HTTP status: 200 (LINE push succeeded)"
} else {
    Write-Output "LINE HTTP status: $($response.StatusCode)"
}
