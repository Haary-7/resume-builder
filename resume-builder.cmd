@echo off
if /I "%~1"=="setup_guide" (
  type "%~dp0SETUP.md"
  exit /b 0
)
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 "%~dp0studio.py" %*
) else (
  python "%~dp0studio.py" %*
)
