@echo off
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 "%~dp0studio.py" start
) else (
  python "%~dp0studio.py" start
)
pause
