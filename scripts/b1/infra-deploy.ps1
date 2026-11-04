param([ValidateSet('core','ia','integracoes')][string]$Component, [Parameter(Mandatory=$true)][string]$Artifacts)
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSEdition -eq 'Desktop') { $env:PSModulePath = "$env:WINDIR/System32/WindowsPowerShell/v1.0/Modules;$env:ProgramFiles/WindowsPowerShell/Modules" }
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$runtime = Join-Path $root 'infra/.runtime'
$Artifacts = (Resolve-Path -LiteralPath $Artifacts).Path
$artifactName = if ($Component -eq 'core') { 'app.jar' } else { 'app.zip' }
foreach ($required in @($artifactName,'source-commit.txt','test-result.txt')) {
    if (-not (Test-Path -LiteralPath (Join-Path $Artifacts $required) -PathType Leaf)) { throw "Deployment artifact missing before service stop: $required" }
}
$destination = Join-Path $runtime $Component
New-Item -ItemType Directory -Force -Path $destination | Out-Null
$pidFile = Join-Path $runtime "$Component.pid"
if (Test-Path $pidFile) {
    & "$PSScriptRoot/infra-component-stop.ps1" -Component $Component
    Start-Sleep -Milliseconds 600
}
if ($Component -eq 'core') {
    Copy-Item -LiteralPath "$Artifacts/app.jar" -Destination "$destination/app.jar" -Force
    $javaHome = ((& cmd.exe /d /c 'java -XshowSettings:properties -version 2>&1' | Select-String '^\s+java.home = ').ToString() -split '=', 2)[1].Trim()
    $exe = Join-Path $javaHome 'bin/java.exe'
    $arguments = '-jar "{0}" --spring.profiles.active=lab --server.address=127.0.0.1 --server.port=8080' -f "$destination/app.jar"
    $port = 8080
    $cwd = $root
} else {
    Expand-Archive -LiteralPath "$Artifacts/app.zip" -DestinationPath $destination -Force
    $exe = Join-Path $root 'services/ia/.venv/Scripts/python.exe'
    $port = if ($Component -eq 'ia') { 8001 } else { 8002 }
    $arguments = "-m uvicorn app.main:app --host 127.0.0.1 --port $port"
    $cwd = $destination
    $env:CORE_BASE_URL = 'http://127.0.0.1:8080'
    $env:MQTT_HOST = '127.0.0.1'
    $env:MQTT_PORT = '1883'
    $env:B1_DB_PATH = "$runtime/integracoes/integracoes.sqlite3"
    $env:B1_MQTT_ENABLED = 'true'
}
$env:JENKINS_NODE_COOKIE = 'b1-native-service'
$process = Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $cwd -WindowStyle Hidden -PassThru -RedirectStandardOutput "$runtime/$Component.stdout.log" -RedirectStandardError "$runtime/$Component.stderr.log"
Set-Content -LiteralPath $pidFile -Value $process.Id
$healthy = $false
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    Start-Sleep -Seconds 1
    if ($process.HasExited) { throw "$Component exited on deployment; see $runtime/$Component.stderr.log" }
    try {
        $healthPath = if ($Component -eq 'core') { '/actuator/health' } else { '/health' }
        $health = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$port$healthPath" -TimeoutSec 2
        if ($health.StatusCode -eq 200) { $healthy = $true; break }
    } catch { }
}
if (-not $healthy) { throw "Deployed $Component did not become healthy" }
Get-Date -Format o | Set-Content "$destination/deployed-at.txt"
Copy-Item -LiteralPath "$Artifacts/source-commit.txt" -Destination "$destination/source-commit.txt" -Force
$lastGood = Join-Path $runtime "last-good/$Component"
New-Item -ItemType Directory -Force -Path $lastGood | Out-Null
if (-not $Artifacts.Equals([System.IO.Path]::GetFullPath($lastGood), [StringComparison]::OrdinalIgnoreCase)) {
    Get-ChildItem -LiteralPath $Artifacts -File | Copy-Item -Destination $lastGood -Force
}
Copy-Item -LiteralPath "$destination/deployed-at.txt" -Destination "$lastGood/deployed-at.txt" -Force
Write-Output "DEPLOY SUCCESS: $Component PID=$($process.Id) http://127.0.0.1:$port"
