param(
    [ValidateSet('core','ia','integracoes')][string]$Component,
    [ValidateSet('Test','Build','Deploy')][string]$Stage,
    [string]$ControlledFailure = '$false'
)
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSEdition -eq 'Desktop') { $env:PSModulePath = "$env:WINDIR/System32/WindowsPowerShell/v1.0/Modules;$env:ProgramFiles/WindowsPowerShell/Modules" }
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$workspace = if ($env:WORKSPACE) { $env:WORKSPACE } else { throw 'Run this script from its Jenkins job' }
$work = Join-Path $workspace 'source'
$artifacts = Join-Path $workspace 'artifacts'
$python = Join-Path $root 'services/ia/.venv/Scripts/python.exe'
if ($Stage -eq 'Test') {
    # Only the job's disposable source/artifacts directories may be replaced.
    foreach ($path in @($work, $artifacts)) {
        $resolved = [System.IO.Path]::GetFullPath($path)
        if (-not $resolved.StartsWith([System.IO.Path]::GetFullPath($workspace) + [System.IO.Path]::DirectorySeparatorChar)) { throw 'Unsafe Jenkins workspace path' }
        if (Test-Path $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
        New-Item -ItemType Directory -Path $resolved -Force | Out-Null
    }
    & git.exe -C $root rev-parse HEAD | Set-Content "$artifacts/source-commit.txt"
    & git.exe -C $root status --short --untracked-files=normal | Set-Content "$artifacts/source-worktree-status.txt"
    Get-Date -Format o | Set-Content "$artifacts/build-started.txt"
    if ($Component -eq 'core') {
        foreach ($name in @('src','.mvn','pom.xml','mvnw.cmd')) { Copy-Item -LiteralPath (Join-Path $root $name) -Destination $work -Recurse -Force }
        if ($ControlledFailure -eq '$true') {
            $failure = Join-Path $work 'src/test/java/com/example/devops/B1ControlledFailureTest.java'
            'package com.example.devops; import org.junit.jupiter.api.Test; import static org.junit.jupiter.api.Assertions.fail; class B1ControlledFailureTest { @Test void blocksDeploy() { fail("B1 expected controlled failure: deployment must be skipped"); } }' | Set-Content -LiteralPath $failure
        }
        Push-Location -LiteralPath $work
        try { & '.\mvnw.cmd' clean verify; if ($LASTEXITCODE -ne 0) { throw "Core verification failed ($LASTEXITCODE); deployment blocked" } } finally { Pop-Location }
    } else {
        $pythonSource = Join-Path $work "services/$Component"
        New-Item -ItemType Directory -Path $pythonSource -Force | Out-Null
        Get-ChildItem -LiteralPath (Join-Path $root "services/$Component") -Force | Where-Object Name -NotIn @('.venv','__pycache__','.pytest_cache','data') | Copy-Item -Destination $pythonSource -Recurse -Force
        if ($ControlledFailure -eq '$true') {
            'def test_b1_controlled_failure():', '    assert False, "B1 expected controlled failure: deployment must be skipped"' | Set-Content -LiteralPath "$pythonSource/tests/test_b1_controlled_failure.py"
        }
        Push-Location -LiteralPath $pythonSource
        try { & $python -m pytest -v; if ($LASTEXITCODE -ne 0) { throw "Python verification failed ($LASTEXITCODE); deployment blocked" } } finally { Pop-Location }
    }
    $manifest = foreach ($sourceFile in (Get-ChildItem -LiteralPath $work -File -Recurse | Where-Object FullName -NotMatch '[\\/](target|__pycache__|\.pytest_cache)[\\/]')) {
        $stream = [System.IO.File]::OpenRead($sourceFile.FullName)
        try { $sha = [System.Security.Cryptography.SHA256]::Create(); $hex = ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', ''); "$hex  $($sourceFile.FullName.Substring($work.Length + 1))" } finally { $stream.Dispose(); $sha.Dispose() }
    }
    $manifest | Set-Content "$artifacts/source-sha256.txt"
    'PASS: real component test suite completed' | Set-Content "$artifacts/test-result.txt"
}
if ($Stage -eq 'Build') {
    if (-not (Test-Path "$artifacts/test-result.txt")) { throw 'Missing successful test gate' }
    if ($Component -eq 'core') {
        $jar = Get-ChildItem -LiteralPath "$work/target" -Filter '*.jar' | Select-Object -First 1
        if (-not $jar) { throw 'Packaged application JAR missing' }
        Copy-Item -LiteralPath $jar.FullName -Destination "$artifacts/app.jar" -Force
    } else {
        Compress-Archive -Path "$work/services/$Component/app" -DestinationPath "$artifacts/app.zip" -Force
    }
    $hashes = foreach ($file in (Get-ChildItem -Path "$artifacts/app.*" -File)) {
        $stream = [System.IO.File]::OpenRead($file.FullName)
        try { $sha = [System.Security.Cryptography.SHA256]::Create(); $hex = ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', ''); "$hex  $($file.Name)" } finally { $stream.Dispose(); $sha.Dispose() }
    }
    $hashes | Set-Content "$artifacts/sha256.txt"
    Write-Output "BUILD COMPLETE: native $Component artifact (container engine unavailable)"
}
if ($Stage -eq 'Deploy') {
    if (-not (Test-Path "$artifacts/test-result.txt")) { throw 'Missing successful test gate' }
    & "$PSScriptRoot/infra-deploy.ps1" -Component $Component -Artifacts $artifacts
}
