@echo off
chcp 65001 >nul
title Compilador - Publicador Redes AutomaPro
cd /d "%~dp0"

echo.
echo ============================================================
echo     COMPILADOR - PUBLICADOR REDES AUTOMAPRO
echo ============================================================
echo.
echo Este script compila todos los ejecutables del proyecto.
echo Asegurate de tener PyInstaller instalado.
echo.
pause

set PYINSTALLER=py -m PyInstaller
set DATOS_BASE=--add-data "compartido;compartido" --add-data "iconos;iconos" --add-data "config_global.txt;." --add-data "version.txt;."
set FLAGS=--onefile --windowed --noconfirm

echo.
echo [1/6] Compilando PublicadorRedes.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --add-data "publicadores;publicadores" --add-data "anuncios;anuncios" --icon=iconos/dashboard.ico --name PublicadorRedes publicar_redes.py
echo.

echo [2/6] Compilando PanelControlRedes.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --icon=iconos/dashboard.ico --name PanelControlRedes panel_control.py
echo.

echo [3/6] Compilando WizardPublicador.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --add-data "anuncios;anuncios" --icon=iconos/wizard.ico --name WizardPublicador wizard_primera_vez.py
echo.

echo [4/6] Compilando ConfiguradorRedes.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --icon=iconos/settings.ico --name ConfiguradorRedes configurador_gui.py
echo.

echo [5/6] Compilando GestorAnuncios.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --add-data "anuncios;anuncios" --icon=iconos/anuncios.ico --name GestorAnuncios gestor_anuncios.py
echo.

echo [6/6] Compilando GestorTareasRedes.exe...
%PYINSTALLER% %FLAGS% %DATOS_BASE% --icon=iconos/calendar.ico --name GestorTareasRedes gestor_tareas_gui.py
echo.

echo ============================================================
echo  COMPILACION COMPLETADA
echo  Los .exe estan en la carpeta: dist\
echo ============================================================
echo.
pause