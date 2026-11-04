# Capture real monitoring data; run after the failure/recovery experiments.
param([int]$Minutes = 15)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$destination = Join-Path $root 'infra/evidencias'
New-Item -ItemType Directory -Force $destination | Out-Null
$end = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$start = $end - $Minutes * 60
$results = [ordered]@{observadoEm=(Get-Date -Format o); inicioUnix=$start; fimUnix=$end; passoSegundos=5; consultas=[ordered]@{}}
$queries = @('b1_ia_falhas_total','b1_notificacoes_pendentes','up{job="core"}','sum(rate(http_server_requests_seconds_count{job="core",uri!="/actuator/prometheus"}[1m]))')
foreach ($query in $queries) {
    $encoded = [uri]::EscapeDataString($query)
    $results.consultas[$query] = Invoke-RestMethod -Uri "http://127.0.0.1:9090/api/v1/query_range?query=$encoded&start=$start&end=$end&step=5"
}
$results | ConvertTo-Json -Depth 16 | Set-Content "$destination/prometheus-series.json"
Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:9090/api/v1/targets' -OutFile "$destination/prometheus-targets.json"
$observed = foreach ($query in @('b1_ia_falhas_total','b1_notificacoes_pendentes')) {
    $values = @($results.consultas[$query].data.result | ForEach-Object { $_.values | ForEach-Object { [double]$_[1] } })
    [ordered]@{metrica=$query; amostras=$values.Count; minimo=($values | Measure-Object -Minimum).Minimum; maximo=($values | Measure-Object -Maximum).Maximum}
}
$observed | ConvertTo-Json -Depth 5 | Set-Content "$destination/prometheus-resumo.json"
$observed | ForEach-Object { [PSCustomObject]$_ } | Format-Table
