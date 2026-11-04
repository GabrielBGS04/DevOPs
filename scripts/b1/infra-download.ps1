# Downloads are pinned to official distributor URLs; run before infra-start.ps1.
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Set-Location -LiteralPath $root
New-Item -ItemType Directory -Force tools | Out-Null
$downloads = @{
    'jenkins.war' = 'https://get.jenkins.io/war-stable/2.580.2/jenkins.war'
    'jenkins-plugin-manager.jar' = 'https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/2.13.2/jenkins-plugin-manager-2.13.2.jar'
    'prometheus.zip' = 'https://github.com/prometheus/prometheus/releases/download/v3.7.3/prometheus-3.7.3.windows-amd64.zip'
    'grafana.zip' = 'https://dl.grafana.com/oss/release/grafana-12.3.0.windows-amd64.zip'
    'mosquitto-installer.exe' = 'https://mosquitto.org/files/binary/win64/mosquitto-2.0.22-install-windows-x64.exe'
}
foreach ($file in $downloads.Keys) {
    if (-not (Test-Path "tools/$file")) {
        & curl.exe -fL --retry 2 -o "tools/$file" $downloads[$file]
        if ($LASTEXITCODE -ne 0) { throw "Download failed: $file" }
    }
}
$sevenZip = Join-Path ${env:ProgramFiles} '7-Zip/7z.exe'
if (-not (Test-Path $sevenZip)) { throw '7-Zip is required to extract the official Mosquitto installer without installing a Windows service' }
foreach ($archive in @('prometheus.zip','grafana.zip')) {
    & $sevenZip x "tools/$archive" '-otools' -y
    if ($LASTEXITCODE -ne 0) { throw "Extraction failed: $archive" }
}
& $sevenZip x tools/mosquitto-installer.exe '-otools/mosquitto' -y
if ($LASTEXITCODE -ne 0) { throw 'Mosquitto extraction failed' }
& java.exe -jar tools/jenkins-plugin-manager.jar --war tools/jenkins.war --plugin-download-directory infra/.runtime/jenkins/plugins --plugin-file infra/jenkins/plugins.txt
if ($LASTEXITCODE -ne 0) { throw 'Jenkins plugin installation failed' }
Get-FileHash -Path tools/jenkins.war,tools/prometheus.zip,tools/grafana.zip,tools/mosquitto-installer.exe -Algorithm SHA256 | Format-List | Out-File tools/download-sha256.txt
