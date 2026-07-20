@echo off
cd /d "%~dp0"
title InvoiceFlow
echo.
echo   InvoiceFlow - Dropbox file storage
echo   ==================================
echo.
echo   Data is saved to data.json in this folder
echo   (Dropbox will sync it to the cloud).
echo.
echo   Open this address if the browser does not open:
echo.
echo       http://127.0.0.1:8765
echo.
echo   Leave this window open while you work.
echo   Press Ctrl+C when finished.
echo.

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" http://127.0.0.1:8765
  py -3 server.py
  goto :eof
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" http://127.0.0.1:8765
  python server.py
  goto :eof
)

echo   Python was not found.
echo   Install Python 3 from https://www.python.org/downloads/
echo   On the installer, check "Add python.exe to PATH".
echo.
pause
