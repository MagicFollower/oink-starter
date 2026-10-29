@echo off
setlocal EnableExtensions
rem Python prints UTF-8; without this the Chinese lines come out mojibake on a 936 codepage console
chcp 65001 >nul
rem Harbor local deployment wrapper. Logic lives in harborctl.py (single implementation);
rem this file only forwards arguments so double-click / cmd usage works without encoding traps.
rem Usage:
rem   Harbor.cmd cert      generate self-signed CA + server cert into the VM path /data/harbor-certs
rem   Harbor.cmd config    write harbor.yml from the official template (six keys patched)
rem   Harbor.cmd prepare   run the official goharbor/prepare container to produce common/ + docker-compose.yml
rem   Harbor.cmd up        docker compose -p harbor up -d
rem   Harbor.cmd status    component health + API health + cert-chain check
rem   Harbor.cmd trust     install the CA into %USERPROFILE%\.docker\certs.d for the local daemon
rem   Harbor.cmd verify    login / create project / push / pull / scan judgments
rem   Harbor.cmd down      docker compose -p harbor down
python "%~dp0harborctl.py" %*
exit /b %ERRORLEVEL%
