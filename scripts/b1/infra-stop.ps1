param([string[]]$Components = @('mqtt', 'prometheus', 'grafana', 'jenkins'))
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
foreach ($component in $Components) {
    if ($component -notin @('mqtt','prometheus','grafana','jenkins')) { throw 'Unknown infrastructure component' }
    $pidFile = Join-Path $root "infra/.runtime/$component.pid"
    if (Test-Path $pidFile) {
        $processId = [int](Get-Content -LiteralPath $pidFile)
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            $pidCreated = (Get-Item -LiteralPath $pidFile).LastWriteTimeUtc
            if ([Math]::Abs(($pidCreated - $process.StartTime.ToUniversalTime()).TotalSeconds) -gt 10) { throw 'PID file does not match the laboratory process start time' }
            if ($process.ProcessName -notin @('java','mosquitto','prometheus','grafana')) { throw 'Unexpected laboratory process name' }
            Stop-Process -Id $processId -ErrorAction Stop
        }
        Remove-Item -LiteralPath $pidFile
        Write-Output "$component stopped"
    }
}
