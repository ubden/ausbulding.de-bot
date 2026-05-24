@echo off
chcp 65001 >nul
title AusbildungBot — Build

echo ============================================================
echo  AusbildungBot PyInstaller Build
echo ============================================================
echo.

:: PyInstaller'ı bul
set PYINST=%APPDATA%\Python\Python313\Scripts\pyinstaller.exe
if not exist "%PYINST%" set PYINST=pyinstaller

:: PyInstaller kurulu mu?
"%PYINST%" --version >nul 2>&1
if errorlevel 1 (
    echo [!] PyInstaller bulunamadi, kuruluyor...
    pip install pyinstaller
    set PYINST=%APPDATA%\Python\Python313\Scripts\pyinstaller.exe
)

:: Eski build'i temizle
if exist dist\AusbildungBot (
    echo [*] Eski dist temizleniyor...
    rmdir /s /q dist\AusbildungBot
)
if exist build\ausbildung (
    rmdir /s /q build\ausbildung
)

echo [*] Build basliyor (birkaç dakika sürebilir)...
"%PYINST%" ausbildung.spec --clean -y

if errorlevel 1 (
    echo.
    echo [HATA] Build basarisiz oldu!
    pause
    exit /b 1
)

:: Kurulum betigini dist klasorune kopyala
copy /y kurulum.bat dist\AusbildungBot\kurulum.bat >nul

echo.
echo ============================================================
echo  BUILD TAMAMLANDI  —  156 MB
echo  Konum: dist\AusbildungBot\AusbildungBot.exe
echo.
echo  ONEMLI: Ilk kullanim oncesinde
echo    dist\AusbildungBot\kurulum.bat
echo  calistirarak Chromium tarayicisini yukleyin!
echo ============================================================
echo.
pause
