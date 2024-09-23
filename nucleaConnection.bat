@echo off
start C:\ngrok\ngrok.exe http 5000
timeout /t 10 /nobreak > NUL
start python ngrok_get_url.py