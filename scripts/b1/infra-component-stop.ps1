param([ValidateSet('core','ia','integracoes')][string]$Component)
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSEdition -eq 'Desktop') { $env:PSModulePath = "$env:WINDIR/System32/WindowsPowerShell/v1.0/Modules;$env:ProgramFiles/WindowsPowerShell/Modules" }
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$pidFile = Join-Path $root "infra/.runtime/$Component.pid"
if (Test-Path $pidFile) {
    $processId = [int](Get-Content -LiteralPath $pidFile)
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($process) {
        $pidCreated = (Get-Item -LiteralPath $pidFile).LastWriteTimeUtc
        $started = $process.StartTime.ToUniversalTime()
        if ([Math]::Abs(($pidCreated - $started).TotalSeconds) -gt 10) { throw 'PID file does not match the laboratory process start time' }
        if ($Component -eq 'core') { $expected = $process.ProcessName -eq 'java' }
        else { $expected = $process.ProcessName -eq 'python' -and $process.Path.StartsWith($root) }
        if (-not $expected) { throw 'PID does not identify the expected laboratory executable' }
        & taskkill.exe /PID $processId /T /F
        if ($LASTEXITCODE -ne 0) { throw 'Could not stop the laboratory process tree' }
    }
    Remove-Item -LiteralPath $pidFile
}
Write-Output "$Component stopped (including child interpreter processes)"
