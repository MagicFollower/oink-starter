@echo off
setlocal EnableExtensions
title Docs Site - Local Preview
cd /d "%~dp0"

rem Keep builds offline and use the local Go toolchain.
set "GOTOOLCHAIN=local"
set "GOPROXY=off"

rem Override the port before launching if 8768 is already in use:
rem   set PORT=9000
if not defined PORT set "PORT=8768"

rem HUGO_EXE wins when Hugo is not on PATH.
set "HUGO="
if defined HUGO_EXE if exist "%HUGO_EXE%" set "HUGO=%HUGO_EXE%"
if not defined HUGO (
  for /f "delims=" %%H in ('where hugo 2^>nul') do (
    if not defined HUGO set "HUGO=%%H"
  )
)

echo ============================================================
echo  Docs Site - Local Preview
echo ============================================================
echo  Project : %CD%
echo  URL     : http://127.0.0.1:%PORT%/
echo  Stop    : Ctrl+C in this window
echo.

if not defined HUGO (
  echo [ERROR] hugo.exe was not found.
  echo Set HUGO_EXE to the full path of hugo.exe, then run again:
  echo   set "HUGO_EXE=C:\path\to\hugo.exe"
  echo.
  pause
  exit /b 1
)

echo  Hugo    : %HUGO%
"%HUGO%" version
if errorlevel 1 (
  echo.
  echo [ERROR] Hugo version check failed.
  pause
  exit /b 1
)

echo.
if defined NO_OPEN (
  echo Starting Hugo server without opening a browser...
) else (
  echo Starting Hugo server...
  echo The browser will open when the server is ready.
)
echo.
if defined NO_OPEN (
  "%HUGO%" server --bind 127.0.0.1 --port %PORT% --disableFastRender
) else (
  "%HUGO%" server --bind 127.0.0.1 --port %PORT% --disableFastRender --openBrowser
)
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" (
  echo [ERROR] Hugo server exited with code %RC%.
  echo If the port is busy, set another port and run again:
  echo   set PORT=9000
) else (
  echo Hugo server stopped.
)
echo.
pause
exit /b %RC%
