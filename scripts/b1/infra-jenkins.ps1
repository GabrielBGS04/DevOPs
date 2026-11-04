param([ValidateSet('core','ia','integracoes')][string]$Component = 'ia', [switch]$ControlledFailure)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$url = "http://127.0.0.1:8081/job/b1-$Component"
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$crumb = Invoke-RestMethod -Uri 'http://127.0.0.1:8081/crumbIssuer/api/json' -WebSession $session
$headers = @{}
$headers[$crumb.crumbRequestField] = $crumb.crumb
$next = (Invoke-RestMethod -Uri "$url/api/json").nextBuildNumber
$fail = $ControlledFailure.IsPresent.ToString().ToLowerInvariant()
Invoke-WebRequest -UseBasicParsing -Uri "$url/buildWithParameters?FALHA_CONTROLADA=$fail" -Method Post -WebSession $session -Headers $headers | Out-Null
Write-Output "Jenkins build queued: $url/$next/"
$build = $null
for ($attempt = 0; $attempt -lt 180; $attempt++) {
    Start-Sleep -Seconds 2
    try { $build = Invoke-RestMethod -Uri "$url/$next/api/json"; if (-not $build.building) { break } } catch { }
}
if (-not $build -or $build.building) { throw 'Build did not finish within six minutes; inspect Jenkins' }
$destination = Join-Path $root 'infra/evidencias'
New-Item -ItemType Directory -Force $destination | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri "$url/$next/consoleText" -OutFile "$destination/jenkins-$Component-$next.log"
$build | ConvertTo-Json -Depth 8 | Set-Content "$destination/jenkins-$Component-$next.json"
Write-Output "Result=$($build.result); $url/$next/"
if ($ControlledFailure) {
    if ($build.result -ne 'FAILURE') { throw 'The controlled test failure was not observed' }
} elseif ($build.result -ne 'SUCCESS') { throw 'Jenkins component pipeline failed' }
