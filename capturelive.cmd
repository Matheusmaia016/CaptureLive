@echo off
setlocal
set SCRIPT_DIR=%~dp0
if exist "%SCRIPT_DIR%release\capturelive.exe" (
  "%SCRIPT_DIR%release\capturelive.exe" %*
  exit /b %errorlevel%
)
if exist "%SCRIPT_DIR%dist\capturelive.exe" (
  "%SCRIPT_DIR%dist\capturelive.exe" %*
  exit /b %errorlevel%
)
python -m capturelive %*
endlocal
