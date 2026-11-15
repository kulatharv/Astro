@echo off
title AstroLogic AI — Unified Dev Launcher
color 0E

echo ==========================================================
echo    AstroLogic AI Platform - Unified Dev Launcher
echo ==========================================================
echo.

set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%backend" (
    set "BACKEND_DIR=%SCRIPT_DIR%backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
) else (
    set "BACKEND_DIR=%SCRIPT_DIR%astro-platform\backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%astro-platform\frontend"
)

:: 1. Auto-detect Python Virtual Environment
set "PYTHON_EXE="
if exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    set "PYTHON_EXE=%BACKEND_DIR%\venv\Scripts\python.exe"
) else if exist "%SCRIPT_DIR%venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe"
) else if exist "%SCRIPT_DIR%..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%..\.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [*] Python:   %PYTHON_EXE%
echo [*] Backend:  %BACKEND_DIR%
echo [*] Frontend: %FRONTEND_DIR%
echo.

:: 2. Check Port 8000
netstat -ano | findstr /R ":8000.*LISTENING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [*] Port 8000 is already active (FastAPI Backend running).
) else (
    echo [+] Starting FastAPI Backend on http://127.0.0.1:8000 ...
    start "AstroLogic Backend [FastAPI:8000]" cmd /k "cd /d "%BACKEND_DIR%" && set PYTHONPATH=. && "%PYTHON_EXE%" -m uvicorn gateway.main:app --host 127.0.0.1 --port 8000 --reload"
)

timeout /t 2 /nobreak >nul

:: 3. Check Port 3000
netstat -ano | findstr /R ":3000.*LISTENING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [*] Port 3000 is already active (Next.js Frontend running).
) else (
    echo [+] Starting Next.js Frontend on http://localhost:3000 ...
    start "AstroLogic Frontend [Next.js:3000]" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"
)

timeout /t 4 /nobreak >nul

:: 4. Open default browser
echo [+] Opening Web Browser: http://localhost:3000 ...
start http://localhost:3000

echo.
echo ==========================================================
echo  AstroLogic Services Running:
echo  ---------------------------------------------------------
echo  Frontend UI:  http://localhost:3000
echo  Backend API:  http://127.0.0.1:8000
echo  API Swagger:  http://127.0.0.1:8000/docs
echo  Profile Hub:  http://localhost:3000/en/profile
echo ==========================================================
echo.
pause

