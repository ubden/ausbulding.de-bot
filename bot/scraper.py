import re
from urllib.parse import quote
from playwright.sync_api import Page

BASE_URL = "https://www.ausbildung.de"


def build_search_url(city: str, radius: str, filters: dict = None, keyword: str = "") -> str:
    city_clean    = city.strip()
    keyword_clean = keyword.strip()
    # Format: "{keyword}|{city}" veya "|{city}" (ausbildung.de URL formatı)
    if keyword_clean:
        search_param = quote(f"{keyword_clean}|{city_clean}", safe="")
    else:
        search_param = quote(f"|{city_clean}", safe="")
    url = f"{BASE_URL}/suche/?search={search_param}&radius={radius or '25'}"
    if filters:
        if filters.get("ausbildungsart"):
            url += f"&ausbildungsart={quote(filters['ausbildungsart'])}"
        if filters.get("abschluss"):
            url += f"&abschluss={quote(filters['abschluss'])}"
        if filters.get("branche"):
            url += f"&branche={quote(filters['branche'])}"
    return url


def scrape_jobs(
    page: Page,
    city: str,
    radius: str,
    filters: dict = None,
    keyword: str = "",
    log=None,
    stop_event=None,
) -> list[dict]:
    def _log(msg):
        if log:
            log(msg)

    url = build_search_url(city, radius, filters, keyword=keyword)
    _log(f"İş ilanları aranıyor: {url}")

    try:
        page.goto(url, wait_until="domcontentloaded")
    except Exception as e:
        _log(f"Sayfa yüklenemedi: {e}")
        return []

    _wait_for_initial_jobs(page)

    # Toplam ilan sayısını oku
    total_available = _read_total_count(page)
    if total_available:
        _log(f"Sayfada toplam {total_available} ilan var.")

    # Tüm ilanları yükle: scroll + "Mehr Ergebnisse laden" döngüsü
    _load_all_results(page, total_available, log=_log, stop_event=stop_event)

    if stop_event and stop_event.is_set():
        return []

    # Sayfadaki tüm direkt başvuruları çıkar
    jobs = _extract_direct_jobs(page, _log)
    _log(f"Toplam {len(jobs)} direkt başvuru ilanı bulundu.")
    return jobs


# ── Yardımcı: yükleme ──────────────────────────────────────────────

def _wait_for_initial_jobs(page: Page):
    for sel in [
        "a.js-direct-application-link",
        "[class*='directApplication']",
        "[class*='JobPostingCard']",
        "article",
    ]:
        try:
            page.locator(sel).first.wait_for(state="visible", timeout=10000)
            return
        except Exception:
            continue
    page.wait_for_timeout(3000)


def _read_total_count(page: Page) -> int:
    """Sayfa başlığındaki toplam ilan sayısını oku."""
    try:
        el = page.locator("[data-testid='search-result-title']").first
        text = el.inner_text(timeout=3000)          # "2177 freie Ausbildungsplätze"
        m = re.search(r"(\d[\d\.]+)", text)
        if m:
            return int(m.group(1).replace(".", ""))
    except Exception:
        pass
    return 0


def _count_loaded(page: Page) -> int:
    """Şu an DOM'da kaç direkt başvuru linki var."""
    count = 0
    try:
        count = max(count, page.locator("a.js-direct-application-link").count())
    except Exception:
        pass
    try:
        count = max(count, page.locator("[class*='directApplication']").count())
    except Exception:
        pass
    return count


def _load_all_results(page: Page, total: int, log=None, stop_event=None):
    """
    Scroll + "Mehr Ergebnisse laden" döngüsü.
    total=0 ise sadece scroll ile yüklemeye çalışır.
    """
    def _log(msg):
        if log:
            log(msg)

    no_change = 0
    prev = _count_loaded(page)

    for step in range(200):          # max 200 adım (~binlerce ilan için yeterli)
        if stop_event and stop_event.is_set():
            return

        # Eğer toplam biliniyorsa ve ulaştıysak dur
        if total and prev >= total:
            _log(f"  Tüm {prev} ilan yüklendi.")
            break

        # Sayfayı aşağı kaydır
        try:
            page.mouse.wheel(0, 600)
        except Exception:
            pass

        try:
            page.wait_for_load_state("domcontentloaded", timeout=2000)
        except Exception:
            pass
        page.wait_for_timeout(600)

        # "Mehr Ergebnisse laden" butonu görünüyorsa tıkla
        clicked = _click_mehr_ergebnisse(page)

        if clicked:
            _log(f"  'Mehr Ergebnisse laden' tıklandı — yükleniyor...")
            page.wait_for_timeout(2000)     # yükleme için bekle
            no_change = 0

        current = _count_loaded(page)
        if current != prev:
            _log(f"  Adım {step + 1}: {current} direkt başvuru ilanı yüklendi")
            no_change = 0
            prev = current
        else:
            no_change += 1
            if no_change >= 8 and not clicked:
                # 8 adım değişme yok + buton yok = sayfa bitti
                _log(f"  Yükleme tamamlandı: {current} ilan")
                break

    # Sayfa sonuna son bir gidiş — scroll lazy-load'u bitir
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
    except Exception:
        pass


def _click_mehr_ergebnisse(page: Page) -> bool:
    """'Mehr Ergebnisse laden' butonunu bul ve tıkla. Başarılıysa True döner."""
    try:
        btn = page.locator("button:has-text('Mehr Ergebnisse laden')").first
        if btn.count() > 0 and btn.is_visible() and btn.is_enabled():
            btn.scroll_into_view_if_needed()
            btn.click()
            return True
    except Exception:
        pass
    return False


# ── Yardımcı: veri çıkarma ────────────────────────────────────────

def _extract_direct_jobs(page: Page, log) -> list[dict]:
    """
    DOM'daki tüm direkt başvuru ilanlarını çıkar.
    Öncelik: a.js-direct-application-link (data-vacancy UUID ile)
    Fallback: [class*='directApplication'] badge → parent card
    """
    jobs = []
    seen_ids = set()

    # ── Yöntem 1: js-direct-application-link ─────────────────────
    direct_links = page.locator("a.js-direct-application-link").all()
    if direct_links:
        log(f"  {len(direct_links)} js-direct-application-link işleniyor...")
        for link in direct_links:
            try:
                vacancy_id = link.get_attribute("data-vacancy") or ""
                href       = link.get_attribute("href") or ""
                if not href:
                    continue
                if not vacancy_id:
                    vacancy_id = _id_from_url(href)
                if not vacancy_id or vacancy_id in seen_ids:
                    continue

                apply_url = href if href.startswith("http") else f"{BASE_URL}{href}"
                title, company, location = _text_from_parent(link)

                # DOM'dan boş geldiyse URL slug'ını kullan
                if not title and not company:
                    title, company, location = _parse_url_slug(apply_url)

                jobs.append({
                    "job_id":  vacancy_id,
                    "title":   title,
                    "company": company,
                    "location":location,
                    "url":     apply_url,
                    "is_direct_application": True,
                })
                seen_ids.add(vacancy_id)
            except Exception:
                continue

    # ── Yöntem 2: directApplication badge ─────────────────────────
    badges = page.locator("[class*='directApplication']").all()
    if badges:
        log(f"  {len(badges)} directApplication badge işleniyor (ek)...")
        for badge in badges:
            try:
                href = badge.evaluate("""el => {
                    let node = el;
                    for (let i = 0; i < 12; i++) {
                        node = node.parentElement;
                        if (!node) break;
                        const a = node.querySelector('a.js-direct-application-link, a[href]');
                        if (a) return a.getAttribute('href');
                    }
                    return '';
                }""")
                if not href:
                    continue
                full_url  = href if href.startswith("http") else f"{BASE_URL}{href}"
                job_id    = _id_from_url(full_url)
                if not job_id or job_id in seen_ids:
                    continue

                title, company, location = _text_from_parent(badge)
                # DOM'dan boş geldiyse URL slug'ını kullan
                if not title and not company:
                    title, company, location = _parse_url_slug(full_url)

                jobs.append({
                    "job_id":  job_id,
                    "title":   title,
                    "company": company,
                    "location":location,
                    "url":     full_url,
                    "is_direct_application": True,
                })
                seen_ids.add(job_id)
            except Exception:
                continue

    return jobs


def _text_from_parent(el) -> tuple[str, str, str]:
    """Verilen elementin parent card'ından başlık, şirket, konum çek."""
    try:
        result = el.evaluate("""el => {
            // Kart container'ını bul
            let card = null;
            let node = el;
            for (let i = 0; i < 15; i++) {
                node = node.parentElement;
                if (!node) break;
                const cls = node.className || '';
                const tag = node.tagName;
                if (tag === 'ARTICLE' || tag === 'LI' ||
                    cls.includes('Card') || cls.includes('card') ||
                    cls.includes('Posting') || cls.includes('posting') ||
                    cls.includes('Result') || cls.includes('result') ||
                    cls.includes('Item') || cls.includes('item') ||
                    cls.includes('Vacancy') || cls.includes('vacancy') ||
                    cls.includes('vacancy') || cls.includes('Job')) {
                    card = node;
                    break;
                }
            }
            // Fallback: 8 seviye yukarı
            if (!card) {
                card = el;
                for (let i = 0; i < 8; i++) {
                    if (card.parentElement) card = card.parentElement;
                }
            }
            if (!card) return '||';

            // Yapısal çıkarma: class wildcard ile
            const titleEl = card.querySelector(
                'h2, h3, h4, [class*="title"], [class*="Title"], [class*="jobTitle"], [class*="JobTitle"], [class*="heading"], [class*="Heading"]'
            );
            const companyEl = card.querySelector(
                '[class*="company"], [class*="Company"], [class*="employer"], [class*="Employer"], ' +
                '[class*="subsidiary"], [class*="Subsidiary"], [class*="subsidiaryName"], [class*="brand"]'
            );
            const locationEl = card.querySelector(
                '[class*="location"], [class*="Location"], [class*="city"], [class*="City"], ' +
                '[class*="region"], [class*="Region"], [class*="address"], [class*="ort"]'
            );

            let title   = titleEl   ? titleEl.innerText.trim()   : '';
            let company = companyEl ? companyEl.innerText.trim() : '';
            let loc     = locationEl ? locationEl.innerText.trim() : '';

            // Yapısal bulunamadıysa satır bazlı fallback
            if (!title && !company) {
                const lines = card.innerText.split('\\n')
                    .map(l => l.trim())
                    .filter(l => l.length > 2 && l.length < 150);
                title   = lines[0] || '';
                company = lines[1] || '';
                loc     = lines[2] || '';
            }
            return title + '|' + company + '|' + loc;
        }""")
        parts    = (result or "||").split("|")
        title    = parts[0][:120].strip() if len(parts) > 0 else ""
        company  = parts[1][:80].strip()  if len(parts) > 1 else ""
        location = parts[2][:60].strip()  if len(parts) > 2 else ""
        return title, company, location
    except Exception:
        return "", "", ""


def _id_from_url(url: str) -> str | None:
    m = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", url, re.I)
    if m:
        return m.group(0)
    parts = url.rstrip("/").split("/")
    if len(parts) >= 2:
        return "/".join(parts[-2:])[:80]
    return None


def _parse_url_slug(url: str) -> tuple[str, str, str]:
    """
    URL slug'ından başlık, şirket, konum çıkar.
    Format: /direktbewerbung/{title}-bei-{company}-in-{location}-{uuid}/
    """
    try:
        # Slug kısmını al — direktbewerbung veya stellen URL'leri
        m = re.search(r"/(?:direktbewerbung|stellen|stelle|job)/([^/?#]+)", url, re.I)
        if not m:
            return "", "", ""
        slug = m.group(1).rstrip("/")

        # Sondaki UUID'yi çıkar
        slug = re.sub(
            r"-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            "", slug, flags=re.I
        )

        # "-bei-" ile son konumdan böl → başlık | şirket+konum
        bei = slug.rfind("-bei-")
        if bei >= 0:
            title_slug   = slug[:bei]
            rest         = slug[bei + 5:]
            # "-in-" ile son konumdan böl → şirket | konum
            in_idx = rest.rfind("-in-")
            if in_idx >= 0:
                company_slug  = rest[:in_idx]
                location_slug = rest[in_idx + 4:]
            else:
                company_slug  = rest
                location_slug = ""
        else:
            title_slug    = slug
            company_slug  = ""
            location_slug = ""

        def _fmt(s: str) -> str:
            return " ".join(w.capitalize() for w in s.split("-") if w)

        return _fmt(title_slug), _fmt(company_slug), _fmt(location_slug)
    except Exception:
        return "", "", ""
