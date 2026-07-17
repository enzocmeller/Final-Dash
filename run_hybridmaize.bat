@echo off
REM Refresh ONLY the UNL Hybrid-Maize (Yield Forecasting Center) forecast and rebuild index.html
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python was not found on PATH.
  echo Install Python 3.10+ from https://www.python.org/downloads/ ^(check "Add to PATH"^).
  pause
  exit /b 1
)
python src\update_hybridmaize.py
if errorlevel 1 (
  echo.
  echo Hybrid-Maize refresh failed - see messages above.
  pause
  exit /b 1
)
echo.
echo Opening dashboard...
start "" "%~dp0index.html"
endlocal
