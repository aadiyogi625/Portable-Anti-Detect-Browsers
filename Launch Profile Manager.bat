@echo off
cd /d "%~dp0"

:: Try pythonw first (no console window)
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw "%~dp0profile_launcher_gui.py"
  goto :eof
)

:: Fallback: try pyw
where pyw >nul 2>nul
if %errorlevel%==0 (
  start "" pyw "%~dp0profile_launcher_gui.py"
  goto :eof
)

:: Last resort: python (will show brief CMD flash)
where python >nul 2>nul
if %errorlevel%==0 (
  start "" python "%~dp0profile_launcher_gui.py"
  goto :eof
)

echo Python nahi mila. Python install karke dubara chalaiye.
pause
