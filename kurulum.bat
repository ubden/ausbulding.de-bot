@echo off
chcp 65001 >nul
title AusbildungBot — Chromium Kurulumu

echo ============================================================
echo  AusbildungBot — Ilk Kurulum
echo  Chromium tarayicisi indiriliyor (~150 MB)
echo ============================================================
echo.

:: Bu exe'nin yanindaki playwright_browsers klasorunu kullan
set PLAYWRIGHT_BROWSERS_PATH=%~dp0playwright_browsers

echo [*] Hedef klasor: %PLAYWRIGHT_BROWSERS_PATH%
echo.

:: playwright CLI'yi bul (exe yaninda ya da Python env'de)
set PW_EXE=%~dp0_internal\playwright\_impl\_driver\playwright.exe
if not exist "%PW_EXE%" (
    :: Gelistirme ortami — pip ile kurulu playwright
    set PW_EXE=playwright
)

echo [*] Chromium indiriliyor...
"%PW_EXE%" install chromium

if errorlevel 1 (
    echo.
    echo [!] playwright.exe bulunamadi, Python uzerinden deneniyor...
    python -m playwright install chromium
)

if errorlevel 1 (
    echo.
    echo [HATA] Chromium yuklenemedi.
    echo Python ve Playwright yuklu oldugundan emin olun:
    echo   pip install playwright
    echo   playwright install chromium
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Kurulum tamamlandi! AusbildungBot.exe calistirabilirsiniz.
echo ============================================================
pause
