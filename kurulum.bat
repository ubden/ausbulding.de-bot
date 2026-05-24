@echo off
chcp 65001 >nul
title AusbildungBot — Chromium Kurulumu

echo ============================================================
echo  AusbildungBot — Ilk Kurulum
echo  Chromium tarayicisi indiriliyor (~150 MB)
echo ============================================================
echo.

:: Bu exe'nin yanindaki playwright_browsers klasorunu kullan
set "PLAYWRIGHT_BROWSERS_PATH=%~dp0playwright_browsers"
set "APP_DIR=%~dp0"
set "INTERNAL_DIR=%APP_DIR%_internal"

echo [*] Hedef klasor: %PLAYWRIGHT_BROWSERS_PATH%
echo.

if not exist "%PLAYWRIGHT_BROWSERS_PATH%" (
    mkdir "%PLAYWRIGHT_BROWSERS_PATH%" >nul 2>&1
)

:: PyInstaller paketinin icindeki Playwright driver'i kullan.
:: Kullanici makinesinde Python veya global playwright kurulu olmak zorunda degil.
set "NODE_EXE=%INTERNAL_DIR%\playwright\driver\node.exe"
set "PW_CLI=%INTERNAL_DIR%\playwright\driver\package\cli.js"

echo [*] Chromium indiriliyor...
if exist "%NODE_EXE%" if exist "%PW_CLI%" (
    "%NODE_EXE%" "%PW_CLI%" install chromium
    goto CHECK_INSTALL
)

echo [!] Paket icindeki Playwright driver bulunamadi.
echo     Beklenen:
echo       %NODE_EXE%
echo       %PW_CLI%
echo.
echo [*] Gelistirme ortami fallback deneniyor...
where playwright >nul 2>&1
if not errorlevel 1 (
    playwright install chromium
    goto CHECK_INSTALL
)

python -m playwright install chromium

:CHECK_INSTALL
if errorlevel 1 (
    echo.
    echo [HATA] Chromium yuklenemedi.
    echo Paket eksik olabilir veya internet baglantisi engellenmis olabilir.
    echo Release ZIP'i tam cikardiginizdan ve bu dosyayi
    echo AusbildungBot.exe ile ayni klasorden calistirdiginizdan emin olun.
    echo.
    echo Gelistirme ortami icin:
    echo   pip install playwright
    echo   python -m playwright install chromium
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Kurulum tamamlandi! AusbildungBot.exe calistirabilirsiniz.
echo ============================================================
pause
