@echo off
chcp 65001 >nul
setlocal EnableExtensions

rem ==== PROJECT CONFIG (the only lines that change per site) ====
set "SITE_TITLE=Docs Site - Local Preview"
set "DEFAULT_PORT=8768"
set "PORT_MAX=8787"
set "HUGO_FALLBACK=%USERPROFILE%\tools\hugo\hugo.exe"
set "GO_FALLBACK=%USERPROFILE%\tools\go1.27.3\go\bin"
set "GO_MIN_NOTE=1.27.3"
rem ==== END PROJECT CONFIG ====

title %SITE_TITLE%
cd /d "%~dp0"

rem Keep builds offline and use the local Go toolchain.
set "GOTOOLCHAIN=local"
set "GOPROXY=off"

rem Hugo: HUGO_EXE wins, then PATH, then HUGO_FALLBACK.
set "HUGO="
if defined HUGO_EXE if exist "%HUGO_EXE%" set "HUGO=%HUGO_EXE%"
if not defined HUGO (
  for /f "delims=" %%H in ('where hugo 2^>nul') do (
    if not defined HUGO set "HUGO=%%H"
  )
)
if not defined HUGO if exist "%HUGO_FALLBACK%" set "HUGO=%HUGO_FALLBACK%"

rem Go: GO_BIN wins, then GO_FALLBACK, then PATH.
set "GO="
if defined GO_BIN if exist "%GO_BIN%\go.exe" set "GO=%GO_BIN%\go.exe"
if not defined GO if exist "%GO_FALLBACK%\go.exe" (
  set "GO=%GO_FALLBACK%\go.exe"
  set "GO_BIN=%GO_FALLBACK%"
)
if not defined GO (
  for /f "delims=" %%G in ('where go 2^>nul') do (
    if not defined GO set "GO=%%G"
  )
)
if defined GO_BIN if exist "%GO_BIN%\go.exe" set "PATH=%GO_BIN%;%PATH%"

rem Port: an explicit PORT is trusted; otherwise probe DEFAULT_PORT..PORT_MAX.
set "PORT_EXPLICIT="
if defined PORT set "PORT_EXPLICIT=1"
if not defined PORT set "PORT=%DEFAULT_PORT%"
if defined PORT_EXPLICIT goto :port_ready
:probe_port
netstat -ano -p tcp | findstr /R /C:":%PORT% .*LISTENING" >nul 2>nul
if errorlevel 1 goto :port_ready
set /a PORT+=1
if %PORT% GTR %PORT_MAX% goto :port_busy
goto :probe_port
:port_busy
echo ============================================================
echo  %SITE_TITLE%
echo ============================================================
echo [ERROR] No free port found between %DEFAULT_PORT% and %PORT_MAX%.
echo Set a port explicitly, then run again:
echo   set PORT=9000
echo.
if not defined NO_PAUSE pause
exit /b 1
:port_ready

echo ============================================================
echo  %SITE_TITLE%
echo ============================================================
echo  Project : %CD%
echo  URL     : http://127.0.0.1:%PORT%/
echo  Stop    : Ctrl+C in this window
if not defined PORT_EXPLICIT if not "%PORT%"=="%DEFAULT_PORT%" echo  Note    : port %DEFAULT_PORT% was busy, using %PORT%.
echo.

if not defined HUGO (
  echo [ERROR] hugo.exe was not found.
  echo Set HUGO_EXE to the full path of hugo.exe, then run again:
  echo   set "HUGO_EXE=C:\path\to\hugo.exe"
  echo.
  if not defined NO_PAUSE pause
  exit /b 1
)

for /f "delims=" %%V in ('"%HUGO%" version 2^>nul') do set "HVER=%%V"
if not defined HVER (
  echo [ERROR] Hugo version check failed.
  echo.
  if not defined NO_PAUSE pause
  exit /b 1
)
echo  Hugo    : %HUGO%
echo            %HVER%
echo %HVER% | findstr /I /C:"extended" >nul
if errorlevel 1 (
  echo.
  echo [ERROR] Hugo Extended is required for this site.
  echo Install Hugo Extended, then run again.
  echo.
  if not defined NO_PAUSE pause
  exit /b 1
)

if not defined GO (
  echo [WARN] go.exe was not found; Hugo module resolution may fail.
  echo Set GO_BIN to the Go bin directory, then run again:
  echo   set "GO_BIN=C:\path\to\go\bin"
  echo.
) else (
  echo  Go      : %GO%
  "%GO%" version
  echo  Note    : Go %GO_MIN_NOTE% or newer is required by go.mod.
  echo.
)

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
if not defined NO_PAUSE pause
exit /b %RC%
