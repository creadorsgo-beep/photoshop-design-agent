@echo off
cd /d "C:\Users\Estudio Creador\Desktop\Claudecodetest"
set LOGFILE=logs\youtube_post_%date:~-4,4%%date:~-7,2%%date:~0,2%.log
"C:\Users\Estudio Creador\AppData\Local\Programs\Python\Python314\python.exe" scripts\youtube_daily_post.py >> "%LOGFILE%" 2>&1
