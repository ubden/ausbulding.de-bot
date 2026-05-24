import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

BASE_URL = "https://www.ausbildung.de"
HOME_URL = f"{BASE_URL}/"

EMAIL_SELECTOR = (
    "input[type='email'], "
    "input[name='email'], "
    "input#email, "
    "input[autocomplete='email'], "
    "input[placeholder*='E-Mail'], "
    "input[placeholder*='Mail']"
)
PASSWORD_SELECTOR = (
    "input[type='password'], "
    "input[name='password'], "
    "input#password, "
    "input[autocomplete='current-password'], "
    "input[placeholder*='Passwort']"
)


def login(page: Page, email: str, password: str, log=None) -> bool:
    def _log(msg):
        if log:
            log(msg)

    _log("Ausbildung.de açılıyor...")
    if not _open_home(page, _log):
        return False
    page.wait_for_timeout(1200)

    # ── Cookie banner ──────────────────────────────────────────────
    _dismiss_cookies(page, _log, timeout_ms=8000)

    # Cookie kapandıktan sonra sayfanın stabilize olmasını bekle
    page.wait_for_timeout(1200)

    # Zaten giriş yapılmış mı?
    if _is_logged_in(page):
        _log("Zaten giriş yapılmış.")
        return True

    # ── Adım 1-2: Login formunu aç ────────────────────────────────
    if not _open_login_form(page, _log):
        _log("Giriş ekranı otomatik açılamadı. Tarayıcıda manuel giriş için 90 sn bekleniyor...")
        if _wait_for_login_form_or_session(page, timeout_ms=90000):
            if _is_logged_in(page):
                _log("Manuel giriş tamamlandı.")
                return True
        else:
            _log("Giriş ekranı bulunamadı.")
            return False

    # ── Adım 3: Modal form ────────────────────────────────────────
    _log("E-posta dolduruluyor...")
    try:
        email_input = _visible_locator(page, EMAIL_SELECTOR)
        if email_input is None:
            page.locator(EMAIL_SELECTOR).first.wait_for(state="visible", timeout=10000)
            email_input = _visible_locator(page, EMAIL_SELECTOR) or page.locator(EMAIL_SELECTOR).first
        email_input.click()
        email_input.fill(email)
        page.wait_for_timeout(500)
    except Exception as e:
        _log(f"E-posta alanı bulunamadı: {e}")
        return False

    _log("Şifre dolduruluyor...")
    try:
        pass_input = _visible_locator(page, PASSWORD_SELECTOR)
        if pass_input is None:
            page.locator(PASSWORD_SELECTOR).first.wait_for(state="visible", timeout=8000)
            pass_input = _visible_locator(page, PASSWORD_SELECTOR) or page.locator(PASSWORD_SELECTOR).first
        pass_input.click()
        pass_input.fill(password)
        page.wait_for_timeout(500)
    except Exception as e:
        _log(f"Şifre alanı bulunamadı: {e}")
        return False

    # ── Adım 4: Submit ────────────────────────────────────────────
    _log("Giriş gönderiliyor...")
    try:
        submit = _visible_locator(
            page,
            "button[type='submit']:has-text('Einloggen'), "
            "button[type='submit'], "
            "button:has-text('Einloggen')"
        )
        if submit is None:
            page.locator("button[type='submit']").first.wait_for(state="visible", timeout=5000)
            submit = _visible_locator(page, "button[type='submit']") or page.locator("button[type='submit']").first
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
        email_still_visible = _visible_locator(page, EMAIL_SELECTOR)
        if email_still_visible is not None:
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


def _open_home(page: Page, log) -> bool:
    """Ana sayfayı ağın tamamen susmasını beklemeden aç."""
    last_error = None

    for wait_until, timeout in (
        ("domcontentloaded", 45000),
        ("load", 30000),
        ("commit", 15000),
    ):
        try:
            page.goto(HOME_URL, wait_until=wait_until, timeout=timeout)
            _wait_for_usable_page(page)
            return True
        except PlaywrightTimeoutError as e:
            last_error = e
            if _page_has_body(page):
                log("Sayfa tam yüklenme sinyalini vermedi; görünen içerikle devam ediliyor.")
                return True
            log(f"Ana sayfa zaman aşımı ({wait_until}), tekrar deneniyor...")
        except Exception as e:
            last_error = e
            if "Target page" in str(e) or "has been closed" in str(e):
                raise
            if _page_has_body(page):
                log("Sayfa yükleme hatası verdi; görünen içerikle devam ediliyor.")
                return True
            log(f"Ana sayfa yükleme hatası ({wait_until}): {e}")

    log(f"Ausbildung.de açılamadı: {last_error}")
    return False


def _wait_for_usable_page(page: Page):
    try:
        page.locator("body").wait_for(state="attached", timeout=8000)
    except Exception:
        pass

    deadline = time.time() + 8
    body_seen = False
    while time.time() < deadline:
        try:
            if _visible_locator(page, "#loginLink") is not None:
                return
            if _visible_locator(page, "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll") is not None:
                return
            if _page_has_body(page):
                body_seen = True
        except Exception:
            pass
        page.wait_for_timeout(300)

    if body_seen:
        return


def _page_has_body(page: Page) -> bool:
    try:
        return page.locator("body").count() > 0
    except Exception:
        return False


def _open_login_form(page: Page, log) -> bool:
    if _login_form_visible(page):
        return True

    _dismiss_cookies(page, log, timeout_ms=1000)

    log("'Anmelden' butonu aranıyor...")
    if _click_first_visible(
        page,
        [
            "#loginLink",
            "button:has-text('Anmelden')",
            "a:has-text('Anmelden')",
            "button[aria-label*='Anmelden']",
            "a[aria-label*='Anmelden']",
        ],
    ) or _click_by_text(page, ["Anmelden"]):
        page.wait_for_timeout(1000)

    if _login_form_visible(page):
        return True

    log("Flyout 'Einloggen' aranıyor...")
    if _click_first_visible(
        page,
        [
            "[class*='loginFlyOutItem']:has-text('Einloggen')",
            "[class*='LoginFlyOut']:has-text('Einloggen')",
            "button:has-text('Einloggen')",
            "a:has-text('Einloggen')",
        ],
    ) or _click_by_text(page, ["Einloggen"]):
        if _wait_for_login_form_or_session(page, timeout_ms=10000):
            return _login_form_visible(page) or _is_logged_in(page)

    # Dar ekran / farklı render durumunda menü üzerinden tekrar dene.
    if _click_first_visible(
        page,
        [
            "button[aria-label*='Menü']",
            "button[aria-label*='Menu']",
            "button[class*='Hamburger']",
            "button[class*='hamburger']",
            "[class*='Hamburger'] button",
        ],
    ):
        page.wait_for_timeout(800)
        if _click_first_visible(
            page,
            [
                "button:has-text('Einloggen')",
                "a:has-text('Einloggen')",
                "button:has-text('Anmelden')",
                "a:has-text('Anmelden')",
            ],
        ) or _click_by_text(page, ["Einloggen", "Anmelden"]):
            if _wait_for_login_form_or_session(page, timeout_ms=10000):
                return _login_form_visible(page) or _is_logged_in(page)

    return _login_form_visible(page)


def _wait_for_login_form_or_session(page: Page, timeout_ms: int = 10000) -> bool:
    elapsed = 0
    while elapsed < timeout_ms:
        if _login_form_visible(page) or _is_logged_in(page):
            return True
        page.wait_for_timeout(400)
        elapsed += 400
    return _login_form_visible(page) or _is_logged_in(page)


def _login_form_visible(page: Page) -> bool:
    return (
        _visible_locator(page, EMAIL_SELECTOR) is not None
        and _visible_locator(page, PASSWORD_SELECTOR) is not None
    )


def _visible_locator(page: Page, selector: str):
    try:
        loc = page.locator(selector)
        for i in range(min(loc.count(), 12)):
            item = loc.nth(i)
            try:
                if item.is_visible():
                    return item
            except Exception:
                continue
    except Exception:
        pass
    return None


def _click_first_visible(page: Page, selectors: list[str]) -> bool:
    for sel in selectors:
        item = _visible_locator(page, sel)
        if item is None:
            continue
        try:
            item.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pass
        try:
            item.click(timeout=5000)
            return True
        except Exception:
            try:
                item.click(timeout=3000, force=True)
                return True
            except Exception:
                continue
    return False


def _click_by_text(page: Page, texts: list[str]) -> bool:
    try:
        clicked = page.evaluate(
            """texts => {
                const wanted = texts.map(t => t.trim().toLowerCase());
                const visible = el => {
                    const style = window.getComputedStyle(el);
                    return style.visibility !== 'hidden' &&
                        style.display !== 'none' &&
                        (el.offsetWidth || el.offsetHeight || el.getClientRects().length);
                };
                const nodes = [...document.querySelectorAll('button, a')];
                const found = nodes.find(el => {
                    if (!visible(el)) return false;
                    const text = (el.innerText || el.textContent || '').trim().toLowerCase();
                    return wanted.some(w => text === w || text.startsWith(w));
                });
                if (!found) return '';
                found.click();
                return (found.innerText || found.textContent || '').trim();
            }""",
            texts,
        )
        return bool(clicked)
    except Exception:
        return False


def _is_logged_in(page: Page) -> bool:
    try:
        current = (page.url or "").lower()
        if "/dashboard/azubi/" in current and "sign_up" not in current:
            return True

        # Login formu görünmüyor = giriş yapılmış
        if _visible_locator(page, EMAIL_SELECTOR) is not None:
            return False  # hâlâ form açık

        # #loginLink yoksa veya görünmüyorsa giriş yapılmış demektir
        anmelden = page.locator("#loginLink").first
        if anmelden.count() > 0 and anmelden.is_visible():
            return False

        for sel in [
            "a[href*='/dashboard/azubi/']",
            "a:has-text('Profil')",
            "button:has-text('Abmelden')",
            "a:has-text('Abmelden')",
            "button:has-text('Logout')",
            "a:has-text('Logout')",
        ]:
            item = _visible_locator(page, sel)
            if item is not None:
                return True

        return False
    except Exception:
        return False  # belirsizse login akışını dene


def _dismiss_cookies(page: Page, log=None, timeout_ms: int = 5000):
    def _log(msg):
        if log:
            log(msg)

    selectors = [
        "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
        "button[id*='AllowAll']",
        "button:has-text('Cookies zulassen')",
        "button:has-text('Alle akzeptieren')",
        "button:has-text('Akzeptieren')",
        "button:has-text('Zustimmen')",
        "button:has-text('Accept all')",
        "button:has-text('Allow all')",
    ]

    deadline = time.time() + (timeout_ms / 1000)
    started = time.time()
    min_wait = min(3.0, max(0.0, timeout_ms / 1000))
    first_try = True
    while first_try or time.time() < deadline:
        first_try = False

        for frame in page.frames:
            try:
                if _click_cookie_in_scope(frame, selectors):
                    _log("Cookie onayı veriliyor...")
                    _wait_cookie_closed(page)
                    return
            except Exception:
                continue

        try:
            clicked = page.evaluate(
                """() => {
                    const patterns = [
                        /cookies zulassen/i,
                        /alle akzeptieren/i,
                        /akzeptieren/i,
                        /zustimmen/i,
                        /accept all/i,
                        /allow all/i
                    ];
                    const visible = el => {
                        const style = window.getComputedStyle(el);
                        return style.visibility !== 'hidden' &&
                            style.display !== 'none' &&
                            (el.offsetWidth || el.offsetHeight || el.getClientRects().length);
                    };
                    const nodes = [...document.querySelectorAll('button, a, input[type="button"], input[type="submit"]')];
                    const found = nodes.find(el => {
                        if (!visible(el)) return false;
                        const text = (el.innerText || el.value || el.textContent || '').trim();
                        return patterns.some(p => p.test(text));
                    });
                    if (!found) return '';
                    found.click();
                    return (found.innerText || found.value || found.textContent || '').trim();
                }"""
            )
            if clicked:
                _log("Cookie onayı veriliyor (JS fallback)...")
                _wait_cookie_closed(page)
                return
        except Exception:
            pass

        if (
            time.time() - started >= min_wait
            and _visible_locator(page, "#loginLink") is not None
            and not _cookie_dialog_visible(page)
        ):
            return
        page.wait_for_timeout(300)


def _click_cookie_in_scope(scope, selectors: list[str]) -> bool:
    for sel in selectors:
        try:
            loc = scope.locator(sel)
            for i in range(min(loc.count(), 6)):
                btn = loc.nth(i)
                if not btn.is_visible():
                    continue
                try:
                    btn.click(timeout=4000)
                    return True
                except Exception:
                    btn.click(timeout=3000, force=True)
                    return True
        except Exception:
            continue
    return False


def _wait_cookie_closed(page: Page):
    page.wait_for_timeout(1000)
    for sel in [
        "#CybotCookiebotDialog",
        "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
    ]:
        try:
            page.locator(sel).first.wait_for(state="hidden", timeout=4000)
            return
        except Exception:
            continue


def _cookie_dialog_visible(page: Page) -> bool:
    for sel in [
        "#CybotCookiebotDialog",
        "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
    ]:
        if _visible_locator(page, sel) is not None:
            return True
    return False
