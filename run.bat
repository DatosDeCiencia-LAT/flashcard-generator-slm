@echo off
cd /d "%~dp0"
echo Iniciando Flashcard Generator...

REM Add GTK to PATH for WeasyPrint
set "PATH=C:\Program Files\GTK3-Runtime Win64\bin;%PATH%"

REM Find Python by checking known locations in order
if exist "C:\Program Files\Python310\python.exe" (
    set PYTHON_EXE=C:\Program Files\Python310\python.exe
    goto :run_app
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
    goto :run_app
)
if exist "C:\Python310\python.exe" (
    set PYTHON_EXE=C:\Python310\python.exe
    goto :run_app
)

echo.
echo ERROR: No se encontro Python en ninguna ubicacion conocida.
echo Ubicaciones buscadas:
echo   C:\Program Files\Python310\python.exe
echo   %LOCALAPPDATA%\Programs\Python\Python310\python.exe
echo   C:\Python310\python.exe
echo.
echo Ejecuta install.bat como administrador para instalarlo.
echo.
pause
exit /b 1

:run_app
echo Usando Python: %PYTHON_EXE%
echo.
"%PYTHON_EXE%" app.py
if %errorlevel% neq 0 (
    echo.
    echo La app cerro con un error. Revisa los mensajes arriba.
    echo.
)
pause
