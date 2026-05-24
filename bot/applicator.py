import os
import time
import random
from playwright.sync_api import Page
from services.openai_service import generate_anschreiben
from services.pdf_service import generate_anschreiben_pdf
from services.database import upsert_contact


def _wait(page: Page, ms: int, stop_event=None):
    """Stop event'i kontrol ederek kısa aralıklarla bekle."""
    chunk = 150
    elapsed = 0
    while elapsed < ms:
        if stop_event and stop_event.is_set():
            return
        page.wait_for_timeout(min(chunk, ms - elapsed))
        elapsed += chunk


def _scroll_to(page: Page, locator):
    try:
        locator.scroll_into_view_if_needed(timeout=3000)
        page.wait_for_timeout(400)
    except Exception:
        pass


def _scroll_page(page: Page, pixels: int = 400):
    page.evaluate(f"window.scrollBy(0, {pixels})")
    page.wait_for_timeout(300)


def apply_to_job(
    page: Page,
    job: dict,
    openai_key: str,
    user_background: str,
    user_info: dict = None,
    log=None,
    stop_event=None,
    skip_pdf_anschreiben: bool = False,
) -> tuple[str, str]:
    """Returns (status, error_message). error_message is '' on success."""
    def _log(msg):
        if log:
            log(msg)

    def _stopped():
        return stop_event and stop_event.is_set()

    title   = job.get("title", "")
    company = job.get("company", "")
    url     = job.get("url", "")
    job_id  = job.get("job_id", "")

    pdf_path: str | None = None   # will be set when a PDF is generated

    _log(f"  → {title} @ {company}")

    def _finish_submission(submitted: bool):
        _log("    Başvuru doğrulanıyor...")
        try:
            page.goto(url, wait_until="domcontentloaded")
            _wait(page, 2500, stop_event)
            if _is_already_applied(page):
                _log("    ✓ Başvuru onaylandı (Bereits beworben görünüyor).")
                return "applied", "", pdf_path
        except Exception:
            pass

        if submitted:
            _log("    Başvuru gönderildi!")
            return "applied", "", pdf_path

        return "error", "Bewerbung abschicken başarısız", pdf_path

    def _submit_if_ready():
        if not _is_on_review_page(page):
            return None
        _log("    Bewerbung abschicken hazır — Überprüfen olmadan direkt onaylanıyor.")
        submitted = _confirm_submit(page, _log, stop_event)
        if _stopped():
            return "skipped", "", pdf_path
        return _finish_submission(submitted)

    try:
        page.goto(url, wait_until="domcontentloaded")
        _wait(page, 2500, stop_event)
        if _stopped():
            return "skipped", "", pdf_path

        ready_result = _submit_if_ready()
        if ready_result:
            return ready_result

        # İlan açıklamasını ve kontakt kişiyi forma girmeden önce al
        job_description = _get_job_description(page)
        contact = _get_contact_person(page)
        if contact and contact.get("email"):
            try:
                upsert_contact(
                    job_id=job_id,
                    company=company,
                    job_title=title,
                    contact_name=contact.get("name", ""),
                    contact_position=contact.get("position", ""),
                    contact_email=contact.get("email", ""),
                    contact_phone=contact.get("phone", ""),
                    job_url=url,
                )
                _log(f"    Kontakt kaydedildi: {contact.get('name')} <{contact.get('email')}>")
            except Exception:
                pass

        # Zaten başvurulmuş mu?
        page.evaluate("window.scrollTo(0, 0)")
        if _is_already_applied(page):
            _log("    Zaten başvurulmuş, atlanıyor.")
            return "already_applied", "", pdf_path

        # Başvuru butonunu bul
        if not _click_apply_button(page, _log, stop_event):
            return "skipped", "", pdf_path

        _wait(page, 3000, stop_event)
        if _stopped():
            return "skipped", "", pdf_path

        ready_result = _submit_if_ready()
        if ready_result:
            return ready_result

        # Form başladı mı?
        if not _is_on_form(page):
            _log("    Başvuru formu yüklenemedi.")
            return "error", "Form yüklenemedi", pdf_path

        # ── Adım 1: Kişisel veriler ────────────────────────────────
        _log("    Adım 1: Kişisel veriler...")
        _wait(page, 1000, stop_event)
        _next_step(page, stop_event)
        if _stopped():
            return "skipped", ""

        # ── Adım 2: İletişim ──────────────────────────────────────
        _log("    Adım 2: İletişim verileri...")
        _wait(page, 1500, stop_event)
        _next_step(page, stop_event)
        if _stopped():
            return "skipped", ""

        # ── Adım 3: Eğitim / Zeugnisse ───────────────────────────
        _log("    Adım 3: Schulische Laufbahn...")
        _wait(page, 1500, stop_event)
        _click_profile_import(page, "Zeugnisse", _log)
        _wait(page, 2000, stop_event)
        _next_step(page, stop_event)
        if _stopped():
            return "skipped", ""

        # ── Adım 4: Anschreiben ───────────────────────────────────
        _log("    Adım 4: Anschreiben kontrol ediliyor...")
        _wait(page, 1500, stop_event)

        # PDF upload gerektiriyor mu? skip_pdf_anschreiben açıksa atla
        if skip_pdf_anschreiben and _has_anschreiben_upload(page):
            _log("    PDF Anschreiben gerekli — 'Anschreiben atla' açık, atlanıyor.")
            return "skipped", "PDF Anschreiben gerekli, atlandı", None

        _click_profile_import(page, "Lebenslauf", _log)
        _wait(page, 1500, stop_event)

        anschreiben = generate_anschreiben(
            title, company, job_description, openai_key, user_background
        )

        if anschreiben:
            # PDF'i her zaman kayıt amacıyla üret; varsa güncel font/metinle yeniden yazar.
            try:
                pdf_path = generate_anschreiben_pdf(
                    anschreiben, title, company, user_info or {}, job_id=job_id
                )
                _log(f"    Anschreiben PDF kaydedildi: {os.path.basename(os.path.dirname(pdf_path))}/")
            except Exception as e:
                _log(f"    PDF oluşturma hatası: {e}")
                pdf_path = None

            # Metin alanını doldur (Kurz-Anschreiben)
            _fill_anschreiben_humanlike(page, anschreiben, _log, stop_event)
            _wait(page, 800, stop_event)

            # PDF upload alanı varsa yükle (zaten oluşturulmuş PDF'i kullan)
            if pdf_path and _has_anschreiben_upload(page):
                _log("    PDF Anschreiben upload alanı bulundu — yükleniyor...")
                _upload_pdf_file(page, pdf_path, _log)
        else:
            _log("    Anschreiben üretilemedi, boş bırakıldı.")

        _select_pdf_anschreiben(page)
        _wait(page, 1000, stop_event)
        _next_step(page, stop_event)
        if _stopped():
            return "skipped", "", pdf_path

        # ── Adım 5: Dosyalar ──────────────────────────────────────
        _log("    Adım 5: Dosyalar kontrol ediliyor...")
        _wait(page, 1500, stop_event)
        _click_profile_import(page, "Lebenslauf", _log)
        _wait(page, 800, stop_event)
        _click_profile_import(page, "Zeugnisse", _log)
        _wait(page, 800, stop_event)
        if _stopped():
            return "skipped", "", pdf_path

        # ── Überprüfen ────────────────────────────────────────────
        review_ok = _click_review(page, _log, stop_event)
        if not review_ok and not _is_on_review_page(page):
            return "error", "Überprüfen butonu bulunamadı", pdf_path

        _wait(page, 2500, stop_event)
        if _stopped():
            return "skipped", "", pdf_path

        # ── Onay ──────────────────────────────────────────────────
        submitted = _confirm_submit(page, _log, stop_event)

        return _finish_submission(submitted)

    except Exception as e:
        if _stopped():
            return "skipped", "", pdf_path
        _log(f"    HATA: {e}")
        return "error", str(e), pdf_path


# ── Yardımcı fonksiyonlar ─────────────────────────────────────────

def _is_already_applied(page: Page) -> bool:
    """Sadece gerçekten tamamlanmış başvuruları atla — devam edenler dahil değil."""
    try:
        btn = page.locator(
            "a.btn-filled__suppressed, "
            "a:has-text('Bereits beworben'), "
            "button:has-text('Bereits beworben')"
        ).first
        return btn.count() > 0 and btn.is_visible()
    except Exception:
        return False


def _click_apply_button(page: Page, log, stop_event=None) -> bool:
    # Öncelik sırası: devam eden başvuru > yeni başvuru
    selectors = [
        # Devam eden direkt başvuru (id veya class ile)
        "#t-link-direct-application-continuation",
        "a.js-direct-application-link",
        "a[id*='continuation']",
        # Yeni başvuru butonları
        "a:has-text('Bewerbung fortführen')",
        "button:has-text('Bewerbung fortführen')",
        "a:has-text('Jetzt bewerben')",
        "button:has-text('Jetzt bewerben')",
        "a:has-text('Bewerben')",
        # Genel CTA (suppressed olanı hariç tut)
        ".cta-button:not(.btn-filled__suppressed)",
    ]

    # Önce viewport'ta ara
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.count() > 0 and btn.is_visible():
                _scroll_to(page, btn)
                btn.click()
                return True
        except Exception:
            continue

    # Bulunamadıysa aşağı kaydırarak tekrar ara (3 tur)
    for _ in range(3):
        if stop_event and stop_event.is_set():
            return False
        _scroll_page(page, 350)
        for sel in selectors:
            try:
                btn = page.locator(sel).first
                if btn.count() > 0 and btn.is_visible():
                    _scroll_to(page, btn)
                    btn.click()
                    return True
            except Exception:
                continue

    log("    Başvuru butonu bulunamadı.")
    return False


def _is_on_form(page: Page) -> bool:
    try:
        indicators = [
            "[class*='Step']", "[class*='step']",
            "[class*='Schritt']", "[data-testid*='step']",
            "input[name*='vorname']", "input[name*='firstName']",
        ]
        for sel in indicators:
            if page.locator(sel).count() > 0:
                return True
    except Exception:
        pass
    return False


def _get_job_description(page: Page) -> str:
    """İlan sayfasındaki tüm anlamlı metni topla."""
    try:
        # Sayfanın tamamını kaydırarak tam içeriği yükle
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(500)
        page.evaluate("window.scrollTo(0, 0)")

        # Önce structured selectors
        for sel in [
            "[class*='jobDescription']", "[class*='JobDescription']",
            "[class*='description']", "[class*='stellenbeschreibung']",
            "article", "main",
        ]:
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    text = el.inner_text().strip()
                    if len(text) > 100:
                        return text[:2000]
            except Exception:
                continue

        # Fallback: body'nin tamamı
        return page.locator("body").inner_text()[:2000]
    except Exception:
        return ""


def _next_step(page: Page, stop_event=None):
    selectors = [
        "button:has-text('Weiter')",
        "button:has-text('Nächste')",
        "button:has-text('Next')",
        "button[type='submit']:not([data-testid='second-button'])",
    ]
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
                _scroll_to(page, btn)
                btn.click()
                _wait(page, 1800, stop_event)
                return
        except Exception:
            continue

    # Scroll edip tekrar dene
    _scroll_page(page, 400)
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
                _scroll_to(page, btn)
                btn.click()
                _wait(page, 1800, stop_event)
                return
        except Exception:
            continue


def _click_profile_import(page: Page, doc_type: str, log):
    text_map = {
        "Zeugnisse": "Zeugnisse aus meinem Profil",
        "Lebenslauf": "Lebenslauf aus meinem Profil",
    }
    text = text_map.get(doc_type, doc_type)
    try:
        btn = page.locator(f"button:has-text('{text}')").first
        if btn.count() > 0:
            _scroll_to(page, btn)
            if btn.is_visible():
                btn.click()
                log(f"    '{text}' profil butonu tıklandı.")
                page.wait_for_timeout(1800)
    except Exception:
        pass


def _fill_anschreiben_humanlike(page: Page, text: str, log, stop_event=None):
    """Anschreiben'i insan gibi — harf harf değil, kelime kelime yaz."""
    selectors = [
        "textarea[name*='anschreiben']", "textarea[name*='coverLetter']",
        "textarea[name*='motivation']", "textarea[placeholder*='Anschreiben']",
        "textarea[placeholder*='Kurz']", "[contenteditable='true']", "textarea",
    ]
    for sel in selectors:
        try:
            area = page.locator(sel).first
            if area.count() == 0 or not area.is_visible():
                continue
            _scroll_to(page, area)
            area.click()
            area.fill("")  # temizle

            # Kelimeleri küçük rastgele gecikmelerle yaz
            words = text.split(" ")
            typed = ""
            for i, word in enumerate(words):
                if stop_event and stop_event.is_set():
                    return
                chunk = word + (" " if i < len(words) - 1 else "")
                area.type(chunk, delay=random.randint(30, 80))
                typed += chunk
                # Her 8-12 kelimede bir kısa mola
                if (i + 1) % random.randint(8, 12) == 0:
                    page.wait_for_timeout(random.randint(200, 500))

            log(f"    Kurz-Anschreiben yazıldı ({len(text)} karakter).")
            return
        except Exception:
            continue
    log("    Anschreiben alanı bulunamadı.")


def _has_anschreiben_upload(page: Page) -> bool:
    """Sayfada Anschreiben için ayrı bir dosya upload alanı var mı kontrol et."""
    try:
        upload_btn = page.locator(
            "button:has-text('Upload Anschreiben'), "
            "label:has-text('Upload Anschreiben'), "
            "label:has-text('Anschreiben hochladen'), "
            "[class*='upload']:has-text('Anschreiben')"
        ).first
        return upload_btn.count() > 0 and upload_btn.is_visible()
    except Exception:
        return False


def _upload_pdf_file(page: Page, pdf_path: str, log):
    """Zaten var olan bir PDF dosyasını Anschreiben upload alanına yükle.
    PDF üretme veya silme işlemi yapmaz — sadece upload eder."""
    if not os.path.exists(pdf_path):
        log("    PDF dosyası bulunamadı — upload atlandı.")
        return

    uploaded = False

    # Yöntem 1: Dropzone içindeki gizli input[type=file]'ı JS ile bul
    try:
        file_handle = page.evaluate_handle("""() => {
            const btns = [...document.querySelectorAll('button')];
            const uploadBtn = btns.find(
                b => b.textContent.trim().includes('Upload Anschreiben')
            );
            if (!uploadBtn) return null;
            let node = uploadBtn;
            for (let i = 0; i < 8; i++) {
                node = node.parentElement;
                if (!node) break;
                const inp = node.querySelector('input[type="file"]');
                if (inp) return inp;
            }
            return null;
        }""")
        el = file_handle.as_element()
        if el is not None:
            el.set_input_files(pdf_path)
            log("    PDF yüklendi ('Upload Anschreiben' dropzone).")
            page.wait_for_timeout(2000)
            uploaded = True
    except Exception:
        pass

    # Yöntem 2: Butona tıklayıp native file chooser yakala
    if not uploaded:
        for sel in [
            "button:has-text('Upload Anschreiben')",
            "label:has-text('Upload Anschreiben')",
        ]:
            try:
                btn = page.locator(sel).first
                if btn.count() == 0 or not btn.is_visible():
                    continue
                _scroll_to(page, btn)
                with page.expect_file_chooser(timeout=6000) as fc_info:
                    btn.click()
                fc_info.value.set_files(pdf_path)
                log("    PDF yüklendi (file chooser).")
                page.wait_for_timeout(2000)
                uploaded = True
                break
            except Exception:
                continue

    if not uploaded:
        log("    PDF upload alanı bulunamadı — manuel yükleme gerekebilir.")


def _select_pdf_anschreiben(page: Page):
    try:
        profile_option = page.locator(
            "button:has-text('Anschreiben aus meinem Profil'), "
            "[class*='profileAnschreiben'], "
            "label:has-text('Profil-Anschreiben')"
        ).first
        if profile_option.count() > 0 and profile_option.is_visible():
            _scroll_to(page, profile_option)
            profile_option.click()
            page.wait_for_timeout(800)
    except Exception:
        pass


def _is_on_review_page(page: Page) -> bool:
    """Gerçek özet/son onay sayfasında mıyız? Sadece submit butonunu kabul et."""
    try:
        loc = page.locator(
            "[data-testid='second-button']:has-text('Bewerbung abschicken'), "
            "button:has-text('Bewerbung abschicken'), "
            "button:has-text('Bewerbung senden'), "
            "button:has-text('Absenden')"
        )
        return loc.count() > 0 and loc.first.is_visible()
    except Exception:
        return False


def _has_submit_success_signal(page: Page) -> bool:
    """Submit sonrası görülen başarı sinyallerini yakala; 431 bu akışta başarılı kabul edilir."""
    try:
        body = page.locator("body").inner_text(timeout=3000).lower()
    except Exception:
        body = ""
    try:
        title = page.title().lower()
    except Exception:
        title = ""
    try:
        url = page.url.lower()
    except Exception:
        url = ""

    blob = "\n".join([body, title, url])
    success_phrases = [
        "erfolgreich beworben",
        "vielen dank",
        "du hast dich beworben",
        "bewerbung gesendet",
        "bewerbung erfolgreich",
    ]
    if any(phrase in blob for phrase in success_phrases):
        return True

    return "431" in blob and any(
        phrase in blob
        for phrase in ("request header", "header fields", "fehler", "error", "431")
    )


def _wait_for_review_page(page: Page, stop_event=None, timeout_ms: int = 12000) -> bool:
    elapsed = 0
    while elapsed < timeout_ms:
        if stop_event and stop_event.is_set():
            return False
        if _is_on_review_page(page):
            return True
        if _has_submit_success_signal(page):
            return True
        page.wait_for_timeout(400)
        elapsed += 400
    return _is_on_review_page(page)


def _get_contact_person(page: Page) -> dict:
    """İlan sayfasındaki kontakt kişi bilgilerini çek."""
    try:
        result = page.evaluate("""() => {
            const container = document.querySelector(
                '.job-posting-contact-person, [class*="contactPerson"], [class*="ContactPerson"]'
            );
            if (!container) return null;

            const nameEl = container.querySelector(
                '.job-posting-contact-person__name, [class*="contactPerson__name"], [class*="ContactName"]'
            );
            const posEl = container.querySelector(
                '.job-posting-contact-person__position, [class*="contactPerson__position"], [class*="ContactPosition"]'
            );
            const emailEl = container.querySelector('a[href^="mailto:"]');
            const phoneEl = container.querySelector('a[href^="tel:"]');

            return {
                name:     nameEl   ? nameEl.innerText.trim()                       : '',
                position: posEl    ? posEl.innerText.trim()                        : '',
                email:    emailEl  ? emailEl.href.replace('mailto:', '').trim()    : '',
                phone:    phoneEl  ? phoneEl.href.replace('tel:', '').trim()       : '',
            };
        }""")
        return result or {}
    except Exception:
        return {}


def _click_review(page: Page, log, stop_event=None) -> bool:
    """Überprüfen butonuna bas — 3 deneme, her seferinde scroll + bekle.
    Aynı data-testid başka adımlarda da kullanıldığı için metne göre ilerler.
    """
    review_selectors = [
        "button:has-text('Überprüfen')",
        "[data-testid='second-button']:has-text('Überprüfen')",
        "button:has-text('Weiter zur Übersicht')",
        "button:has-text('Zur Zusammenfassung')",
        "button:has-text('Weiter zur Zusammenfassung')",
    ]

    for attempt in range(3):
        if stop_event and stop_event.is_set():
            return False

        # Her denemede alta in; Überprüfen genellikle sticky footer'da.
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(400)
        except Exception:
            pass

        for sel in review_selectors:
            try:
                btn = page.locator(sel).first
                if btn.count() == 0:
                    continue
                btn.wait_for(state="visible", timeout=2000)
                if not btn.is_enabled():
                    continue
                _scroll_to(page, btn)
                btn.click()
                log(f"    Überprüfen tıklandı (deneme {attempt + 1}).")
                _wait_for_review_page(page, stop_event, timeout_ms=10000)
                return True
            except Exception:
                continue

        # Ancak gerçek submit butonu görünüyorsa review adımı zaten geçilmiş demektir.
        if _is_on_review_page(page):
            log("    Özet sayfası tespit edildi — Bewerbung abschicken bekleniyor.")
            return True

        log(f"    Überprüfen butonu bulunamadı (deneme {attempt + 1}/3), bekleniyor...")
        page.wait_for_timeout(2000)

    # Son şans: submit butonu var mı?
    if _is_on_review_page(page):
        log("    Özet sayfası tespit edildi — devam ediliyor.")
        return True

    log("    Überprüfen butonu 3 denemede de bulunamadı.")
    return False


def _confirm_submit(page: Page, log, stop_event=None) -> bool:
    """Bewerbung abschicken butonunu bekle, bas ve submit sonrası sonucu doğrula."""
    _wait(page, 800, stop_event)

    confirm_selectors = [
        "[data-testid='second-button']:has-text('Bewerbung abschicken')",
        "button:has-text('Bewerbung abschicken')",
        "button:has-text('Bewerbung senden')",
        "[data-testid='second-button']:has-text('Absenden')",
        "button:has-text('Absenden')",
        "button:has-text('Senden')",
    ]

    submitted = False
    for attempt in range(1, 7):
        if stop_event and stop_event.is_set():
            return False
        if _has_submit_success_signal(page):
            log("    Başvuru başarı sinyali görüldü.")
            return True

        # Sayfanın altına in — buton genellikle sticky footer'da
        try:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(400)
        except Exception:
            pass

        clicked = False
        for sel in confirm_selectors:
            try:
                btn = page.locator(sel).first
                if btn.count() == 0:
                    continue
                btn.wait_for(state="visible", timeout=2000)
                if not btn.is_enabled():
                    continue
                _scroll_to(page, btn)
                btn.click()
                log(f"    'Bewerbung abschicken' tıklandı (deneme {attempt}).")
                clicked = True
                submitted = True
                _wait(page, 3500, stop_event)
                break
            except Exception:
                continue

        if clicked:
            if _has_submit_success_signal(page):
                log("    Başvuru başarı sayfası doğrulandı.")
                return True
            # Başarı metni yoksa 2. onay adımı olabilir — döngü devam eder
        else:
            if attempt < 6:
                log(f"    Onay butonu bekleniyor (deneme {attempt}/6)...")
                page.wait_for_timeout(1500)
            else:
                log("    'Bewerbung abschicken' 6 denemede de bulunamadı.")
                return False

    return submitted
