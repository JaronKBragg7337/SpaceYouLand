@echo off
title Curtis AI Unreal Lab - Claude Code
cd /d "%~dp0"
set TERM=xterm-256color
"%USERPROFILE%\.local\bin\claude.exe"
echo.
echo Claude has closed. You can close this window or press any key.
pause >nul
