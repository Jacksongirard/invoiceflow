@echo off
setlocal
title InvoiceFlow
cd /d "%~dp0"

echo.
echo   InvoiceFlow
echo   ===========
echo.

if not exist "%~dp0app\index.html" (
  echo   ERROR: index.html is not on this PC yet.
  echo   Path: %~dp0app\index.html
  echo.
  echo   In Dropbox, right-click the "app" folder -^> Make available offline.
  echo   Wait for green checkmarks, then run this again.
  echo.
  pause
  exit /b 1
)

if not exist "%~dp0app\server.ps1" (
  echo   ERROR: server.ps1 missing. Wait for Dropbox sync.
  echo.
  pause
  exit /b 1
)

echo   Starting... leave this window open.
echo   Opening http://127.0.0.1:8765/index.html
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -LiteralPath '%~dp0app\server.ps1' -ErrorAction SilentlyContinue"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0app\server.ps1"
echo.
pause
