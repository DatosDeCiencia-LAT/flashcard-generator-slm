@echo off
echo Iniciando Flashcard Generator...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python no esta instalado o no esta en el PATH.
    echo.
    echo Por favor ejecuta primero: install.bat
    echo Haz clic derecho sobre install.bat y selecciona "Ejecutar como administrador"
    echo Luego cierra esta ventana, abre una nueva y vuelve a ejecutar run.bat
    echo.
    pause
    exit /b 1
)

REM Add GTK to PATH so WeasyPrint can find its libraries
if exist "C:\Program Files\GTK3-Runtime Win64\bin" (
    set "PATH=C:\Program Files\GTK3-Runtime Win64\bin;%PATH%"
)

python "%~dp0app.py" > "%~dp0error_log.txt" 2>&1
if %errorlevel% neq 0 (
    echo.
    echo La app cerro con un error. Revisa el archivo error_log.txt en la carpeta de la app.
    echo.
)
pause
