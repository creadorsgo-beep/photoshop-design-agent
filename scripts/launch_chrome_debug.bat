@echo off
:: Lanza Chrome con remote debugging habilitado en el puerto 9222
:: Necesario para que el agente pueda controlar Chrome

set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
set CHROME_ALT="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
set USER_DATA=C:\temp\chrome-debug
set PORT=9222

if not exist %CHROME% (
    if not exist %CHROME_ALT% (
        echo ERROR: No se encontro Chrome. Ajusta la ruta en este script.
        pause
        exit /b 1
    )
    set CHROME=%CHROME_ALT%
)

mkdir %USER_DATA% 2>nul

echo Lanzando Chrome con remote debugging en puerto %PORT%...
echo Abriendo Google Labs Flow...

start "" %CHROME% --remote-debugging-port=%PORT% --user-data-dir=%USER_DATA% https://labs.google/flow/image-generation

echo.
echo Chrome lanzado. Inicia sesion en Google si se pide.
echo El agente ya puede conectarse automaticamente.
