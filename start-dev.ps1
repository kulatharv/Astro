# AstroLogic AI — Unified Development Launcher
# Starts both Backend Gateway (FastAPI) and Frontend UI (Next.js) in separate visible terminal windows.

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
$BackendDir = Join-Path $Root 'astro-platform\backend'
$FrontendDir = Join-Path $Root 'astro-platform\frontend'

Write-Host '==========================================================' -ForegroundColor Cyan
Write-Host '   AstroLogic AI Platform - Unified Dev Launcher' -ForegroundColor Yellow
Write-Host '==========================================================' -ForegroundColor Cyan

# 1. Discover Python Virtual Environment
$venvCandidates = @(
    (Join-Path $BackendDir 'venv\Scripts\python.exe'),
    (Join-Path $Root 'astro-platform\venv\Scripts\python.exe'),
    (Join-Path $Root '.venv\Scripts\python.exe')
)

$PythonExe = 'python'
foreach ($candidate in $venvCandidates) {
    if (Test-Path $candidate) {
        $PythonExe = $candidate
        break
    }
}

Write-Host ('>> Python Path:   ' + $PythonExe) -ForegroundColor Gray
Write-Host ('>> Backend Path:  ' + $BackendDir) -ForegroundColor Gray
Write-Host ('>> Frontend Path: ' + $FrontendDir) -ForegroundColor Gray
Write-Host ''

# 2. Check Port 8000 (Backend)
$port8000Active = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($port8000Active) {
    Write-Host '>> Port 8000 is already active (Backend running).' -ForegroundColor Green
} else {
    Write-Host '>> Launching FastAPI Backend on http://127.0.0.1:8000 ...' -ForegroundColor Cyan
    $backendCmd = 'Set-Location ' + [char]39 + $BackendDir + [char]39 + '; $env:PYTHONPATH=' + [char]39 + '.' + [char]39 + '; & ' + [char]39 + $PythonExe + [char]39 + ' -m uvicorn gateway.main:app --host 127.0.0.1 --port 8000 --reload'
    Start-Process powershell.exe -ArgumentList '-NoExit', '-Command', $backendCmd
}

# 3. Check Port 3000 (Frontend)
$port3000Active = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($port3000Active) {
    Write-Host '>> Port 3000 is already active (Frontend running).' -ForegroundColor Green
} else {
    Write-Host '>> Launching Next.js Frontend on http://localhost:3000 ...' -ForegroundColor Cyan
    $frontendCmd = 'Set-Location ' + [char]39 + $FrontendDir + [char]39 + '; npm run dev'
    Start-Process powershell.exe -ArgumentList '-NoExit', '-Command', $frontendCmd
}

# 4. Open Default Browser
Start-Sleep -Seconds 3
Write-Host '>> Opening Web Browser: http://localhost:3000' -ForegroundColor Green
Start-Process 'http://localhost:3000'

Write-Host '==========================================================' -ForegroundColor Cyan
Write-Host ' Both services are running in their respective terminals.' -ForegroundColor Yellow
Write-Host ' Frontend: http://localhost:3000' -ForegroundColor White
Write-Host ' Backend:  http://127.0.0.1:8000' -ForegroundColor White
Write-Host ' API Docs: http://127.0.0.1:8000/docs' -ForegroundColor White
Write-Host ' Profile:  http://localhost:3000/en/profile' -ForegroundColor White
Write-Host '==========================================================' -ForegroundColor Cyan
