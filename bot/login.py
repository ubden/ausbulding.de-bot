import time
from playwright.sync_api import Page

BASE_URL = "https://www.ausbildung.de"


def login(page: Page, email: str, password: str, log=None) -> bool:
    def _log(msg):
        if log:
            log(msg)

    _log("Ausbildung.de açılıyor...")
    page.goto(BASE_URL, wait_until="networkidle")
    page.wait_for_timeout(2000)

    # ── Cookie banner ──────────────────────────────────────────────
    _dismiss_cookies(page, _log)

    # Cookie kapandıktan sonra sayfanın stabilize olmasını bekle
    page.wait_for_timeout(2500)

    # Zaten giriş yapılmış mı?
    if _is_logged_in(page):
        _log("Zaten giriş yapılmış.")
        return True

    # ── Adım 1: "Anmelden" navbar butonu ──────────────────────────
    _log("'Anmelden' butonuna tıklanıyor...")
    try:
        navbar_btn = page.locator("#loginLink").first
        navbar_btn.wait_for(state="visible", timeout=10000)
        navbar_btn.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        navbar_btn.click()
        page.wait_for_timeout(1500)
    except Exception as e:
        _log(f"Anmelden butonu hatası: {e}")
        return False

    # ── Adım 2: Flyout → "Einloggen" seç ─────────────────────────
    _log("Flyout 'Einloggen' tıklanıyor...")
    try:
        # Flyout item'ı class'ın bir parçasına göre bul
        flyout_btn = page.locator("[class*='loginFlyOutItem']").first
        flyout_btn.wait_for(state="visible", timeout=6000)
        flyout_btn.click()
        page.wait_for_timeout(2000)
    except Exception as e:
        _log(f"Flyout butonu hatası: {e}")
        # Fallback: görünür tüm Einloggen butonlarından ilkini dene
        try:
            fallback = page.get_by_role("button", name="Einloggen").first
            fallback.wait_for(state="visible", timeout=4000)
            fallback.click()
            page.wait_for_timeout(2000)
        except Exception as e2:
            _log(f"Fallback flyout hatası: {e2}")
            return False

    # ── Adım 3: Modal form ────────────────────────────────────────
    _log("E-posta dolduruluyor...")
    try:
        email_input = page.locator(
            "input[type='email'], "
            "input[placeholder*='E-Mail'], "
            "input[name='email']"
        ).first
        email_input.wait_for(state="visible", timeout=10000)
        email_input.click()
        email_input.fill(email)
        page.wait_for_timeout(500)
    except Exception as e:
        _log(f"E-posta alanı bulunamadı: {e}")
        return False

    _log("Şifre dolduruluyor...")
    try:
        pass_input = page.locator(
            "input[type='password'], "
            "input[placeholder*='Passwort']"
        ).first
        pass_input.wait_for(state="visible", timeout=5000)
        pass_input.click()
        pass_input.fill(password)
        page.wait_for_timeout(500)
    except Exception as e:
        _log(f"Şifre alanı bulunamadı: {e}")
        return False

    # ── Adım 4: Submit ────────────────────────────────────────────
    _log("Giriş gönderiliyor...")
    try:
        submit = page.locator("button[type='submit']").first
        submit.wait_for(state="visible", timeout=5000)
        submit.click()
    except Exception as e:
        _log(f"Submit butonu hatası: {e}")
        return False

    _log("Yanıt bekleniyor...")

    # Modal kapanana veya sayfa değişene kadar bekle (max 10 sn)
    try:
        page.wait_for_function(
            """() => {
                // Modal kapatıldıysa form input'ları kaybolur
                const emailInput = document.querySelector('input[type="email"]');
                if (!emailInput || !emailInput.offsetParent) return true;
                // Hata mesajı varsa dur
                const err = document.querySelector('[class*="error"], [class*="Error"]');
                if (err && err.offsetParent && err.innerText.trim()) return true;
                return false;
            }""",
            timeout=10000,
        )
    except Exception:
        pass  # timeout — devam et, URL kontrolüne bak

    page.wait_for_timeout(2000)

    # ── Başarı kontrolü ───────────────────────────────────────────
    # 1. Hata mesajı var mı?
    try:
        err = page.locator("[class*='error'], [class*='Error']").first
        if err.count() > 0 and err.is_visible():
            err_text = err.inner_text().strip()
            if err_text:
                _log(f"Giriş hatası: {err_text}")
                return False
    except Exception:
        pass

    # 2. Login formu hâlâ açık mı? (modal kapanmadıysa başarısız)
    try:
        email_still_visible = page.locator("input[type='email']").first
        if email_still_visible.count() > 0 and email_still_visible.is_visible():
            _log("Giriş başarısız. E-posta/şifre kontrol edin.")
            return False
    except Exception:
        pass

    # 3. URL kontrolü
    current = page.url
    if any(x in current for x in ["confirm", "verify", "bestatigen", "aktivier"]):
        _log("E-posta doğrulama gerekiyor — tarayıcıda tamamlayın.")
        for _ in range(90):
            time.sleep(1)
            try:
                ei = page.locator("input[type='email']").first
                if ei.count() == 0 or not ei.is_visible():
                    _log("Giriş tamamlandı!")
                    return True
            except Exception:
                pass
        _log("Doğrulama zaman aşımı.")
        return False

    # 4. Modal kapandı = başarılı
    _log("Giriş başarılı!")
    return True


def _is_logged_in(page: Page) -> bool:
    try:
        # Login formu görünmüyor = giriş yapılmış
        email_input = page.locator("input[type='email']").first
        if email_input.count() > 0 and email_input.is_visible():
            return False  # hâlâ form açık
        # #loginLink yoksa veya görünmüyorsa giriş yapılmış demektir
        anmelden = page.locator("#loginLink").first
        if anmelden.count() > 0 and anmelden.is_visible():
            return False
        return True
    except Exception:
        return True  # belirsizse devam et


def _dismiss_cookies(page: Page, log=None):
    def _log(msg):
        if log:
            log(msg)

    try:
        btn = page.locator("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        btn.wait_for(state="visible", timeout=8000)
        _log("Cookie onayı veriliyor...")
        btn.click()
        page.wait_for_timeout(1500)
        # Dialog kapanana kadar bekle
        page.locator("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").wait_for(
            state="hidden", timeout=5000
        )
        return
    except Exception:
        pass

    # Fallback
    try:
        btn = page.locator(
            "button:has-text('Cookies zulassen'), "
            "button:has-text('Alle akzeptieren'), "
            "button[id*='AllowAll']"
        ).first
        if btn.count() > 0 and btn.is_visible():
            _log("Cookie onayı veriliyor (fallback)...")
            btn.click()
            page.wait_for_timeout(1500)
    except Exception:
        pass
