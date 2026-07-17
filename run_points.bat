@echo off
REM Refresh ONLY the multi-point corn sampling (forecast weather + soil over each state's top corn areas) and rebuild index.html
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python was not found on PATH.
  echo Install Python 3.10+ from https://www.python.org/downloads/ ^(check "Add to PATH"^).
  pause
  exit /b 1
)
python src\update_points.py
if errorlevel 1 (
  echo.
  echo Multi-point refresh failed - see messages above.
  pause
  exit /b 1
)
echo.
echo Opening dashboard...
start "" "%~dp0index.html"
endlocal
