@echo off
cd /d "%~dp0"
echo Zisu: http://127.0.0.1:8787/
echo Keep this window open while browsing.
node server/index.mjs
pause
