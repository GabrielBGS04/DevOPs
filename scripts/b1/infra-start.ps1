param([string[]]$Components = @('mqtt', 'prometheus', 'grafana', 'jenkins'))
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $root
$runtime = Join-Path $root 'infra/.runtime'
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
function Start-LabProcess($name, $exe, $arguments) {
    $pidFile = Join-Path $runtime "$name.pid"
    if (Test-Path $pidFile) {
        $existing = Get-Process -Id ([int](Get-Content $pidFile)) -ErrorAction SilentlyContinue
        if ($existing) { Write-Output "$name already running PID=$($existing.Id)"; return }
    }
    $process = Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime "$name.stdout.log") -RedirectStandardError (Join-Path $runtime "$name.stderr.log")
    Set-Content -LiteralPath $pidFile -Value $process.Id
    Write-Output "$name started PID=$($process.Id)"
}
if ('mqtt' -in $Components) {
    New-Item -ItemType Directory -Force -Path "$runtime/mqtt" | Out-Null
    Start-LabProcess 'mqtt' "$root/tools/mosquitto/mosquitto.exe" '-c infra/mqtt/mosquitto.conf -v'
}
if ('prometheus' -in $Components) {
    Start-LabProcess 'prometheus' "$root/tools/prometheus-3.7.3.windows-amd64/prometheus.exe" '--config.file=infra/observabilidade/prometheus.yml --storage.tsdb.path=infra/.runtime/prometheus --web.listen-address=127.0.0.1:9090'
}
if ('grafana' -in $Components) {
    New-Item -ItemType Directory -Force -Path "$runtime/grafana/data", "$runtime/grafana/logs", "$runtime/grafana/plugins" | Out-Null
    $env:GF_PATHS_DATA = "$runtime/grafana/data"
    $env:GF_PATHS_LOGS = "$runtime/grafana/logs"
    $env:GF_PATHS_PLUGINS = "$runtime/grafana/plugins"
    $env:GF_PATHS_PROVISIONING = "$root/infra/observabilidade/provisioning"
    Start-LabProcess 'grafana' "$root/tools/grafana-12.3.0/bin/grafana.exe" ('server --homepath="{0}" --config="{1}"' -f "$root/tools/grafana-12.3.0", "$root/infra/observabilidade/grafana.ini")
}
if ('jenkins' -in $Components) {
    $javaHome = ((& cmd.exe /d /c 'java -XshowSettings:properties -version 2>&1' | Select-String '^\s+java.home = ').ToString() -split '=', 2)[1].Trim()
    $env:JENKINS_HOME = "$runtime/jenkins"
    $env:B1_LAB_ROOT = $root
    New-Item -ItemType Directory -Force -Path "$env:JENKINS_HOME/init.groovy.d" | Out-Null
    Copy-Item -LiteralPath 'infra/jenkins/bootstrap.groovy' -Destination "$env:JENKINS_HOME/init.groovy.d/b1.groovy" -Force
    Start-LabProcess 'jenkins' (Join-Path $javaHome 'bin/java.exe') ('-Djenkins.install.runSetupWizard=false -jar "{0}" --httpPort=8081 --httpListenAddress=127.0.0.1' -f "$root/tools/jenkins.war")
}
