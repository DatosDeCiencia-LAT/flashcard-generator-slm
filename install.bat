@echo off
REM Flashcard Generator - Automatic Installer

REM Auto-elevate to administrator if not already elevated
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    PowerShell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ========================================
echo Flashcard Generator - Instalacion
echo ========================================
echo.

REM Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python ya esta instalado
    goto install_deps
)

echo Paso 1: Instalando Python 3.10 (puede tardar varios minutos)...
echo.

REM Write PowerShell script to temp file to avoid line-continuation issues
set PS1=%TEMP%\flashcard_install_python.ps1
(
    echo $ErrorActionPreference = 'Stop'
    echo [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    echo $url = 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe'
    echo $output = "$env:TEMP\python_installer.exe"
    echo Write-Host 'Descargando Python desde python.org...'
    echo ^(New-Object System.Net.WebClient^).DownloadFile^($url, $output^)
    echo Write-Host 'Ejecutando instalador de Python...'
    echo Start-Process $output -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0' -Wait
    echo Remove-Item $output -Force -ErrorAction SilentlyContinue
) > "%PS1%"

PowerShell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set PS_EXIT=%errorlevel%
del "%PS1%" 2>nul

if %PS_EXIT% neq 0 (
    echo.
    echo ERROR: No se pudo instalar Python automaticamente.
    echo Visita https://www.python.org/downloads/ e instala Python 3.10 manualmente.
    echo Durante la instalacion, marca la opcion "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [OK] Python instalado exitosamente

REM Refresh PATH for the current session
set "PATH=C:\Program Files\Python310;C:\Program Files\Python310\Scripts;%PATH%"

:install_gtk
echo.
echo Paso 2: Instalando GTK runtime (necesario para exportar PDF)...
echo.

set GTK_PS1=%TEMP%\flashcard_install_gtk.ps1
(
    echo $ErrorActionPreference = 'Stop'
    echo [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    echo $url = 'https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe'
    echo $output = "$env:TEMP\gtk_installer.exe"
    echo Write-Host 'Descargando GTK runtime...'
    echo ^(New-Object System.Net.WebClient^).DownloadFile^($url, $output^)
    echo Write-Host 'Instalando GTK runtime...'
    echo Start-Process $output -ArgumentList '/S' -Wait
    echo Remove-Item $output -Force -ErrorAction SilentlyContinue
) > "%GTK_PS1%"

PowerShell -NoProfile -ExecutionPolicy Bypass -File "%GTK_PS1%"
set GTK_EXIT=%errorlevel%
del "%GTK_PS1%" 2>nul

if %GTK_EXIT% neq 0 (
    echo AVISO: No se pudo instalar GTK automaticamente.
    echo La exportacion de PDF podria fallar.
    echo Instala manualmente desde:
    echo   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
) else (
    echo [OK] GTK runtime instalado
)

:install_deps
echo.
echo Paso 3: Instalando paquetes requeridos...
echo.

python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ERROR: No se pudo actualizar pip
    pause
    exit /b 1
)

REM Try pre-built wheel for llama-cpp-python first (no compiler needed)
echo Instalando llama-cpp-python (intentando rueda pre-compilada)...
pip install llama-cpp-python==0.3.2 --only-binary :all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
if %errorlevel% neq 0 (
    echo No se encontro rueda pre-compilada. Instalando compilador C++ de Microsoft...
    echo Esto puede tardar 10-20 minutos y requiere ~3 GB de espacio...
    winget install --id Microsoft.VisualStudio.2022.BuildTools --accept-source-agreements --accept-package-agreements --override "--quiet --wait --norestart --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended" 2>nul
    winget install --id Kitware.CMake --accept-source-agreements --accept-package-agreements 2>nul
    echo Compilando llama-cpp-python desde codigo fuente...
    pip install llama-cpp-python==0.3.2 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
    if %errorlevel% neq 0 (
        echo.
        echo AVISO: No se pudo instalar llama-cpp-python automaticamente.
        echo La app no funcionara hasta resolverlo. Instrucciones:
        echo   1. Instala Visual Studio Build Tools desde:
        echo      https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo   2. Selecciona el workload "Desarrollo de escritorio con C++"
        echo   3. Vuelve a ejecutar install.bat
        echo.
        echo Continuando con la instalacion de los demas paquetes...
        echo.
    )
)

REM Always install remaining packages regardless of llama-cpp-python result
echo Instalando paquetes restantes...
pip install --prefer-binary gradio pymupdf easyocr pillow numpy weasyprint huggingface-hub
pip install --prefer-binary llama-index-core llama-index-embeddings-huggingface llama-index-vector-stores-chroma chromadb
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar algunos paquetes
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Instalacion completada!
echo ========================================
echo.
echo Ahora puedes abrir la app haciendo doble clic en:
echo   run.bat
echo.
pause
