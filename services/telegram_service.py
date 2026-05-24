"""
Telegram Bot API — mesaj gönderme servisi.
Harici bağımlılık yok: sadece stdlib urllib kullanılır.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime


_BASE = "https://api.telegram.org/bot{token}/{method}"


def _post(token: str, method: str, payload: dict, timeout: int = 10) -> tuple[bool, str]:
    url  = _BASE.format(token=token, method=method)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req  = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            msg = json.loads(body).get("description", body[:200])
        except Exception:
            msg = body[:200]
        return False, msg
    except Exception as e:
        return False, str(e)


def send_message(
    token: str,
    chat_id: str,
    text: str,
    parse_mode: str = "HTML",
    disable_preview: bool = False,
) -> tuple[bool, str]:
    """
    Telegram botuna mesaj gönder.
    Döner: (True, "") başarı | (False, hata_mesajı) hata
    """
    if not token or not chat_id:
        return False, "Token veya Chat ID eksik"
    return _post(token, "sendMessage", {
        "chat_id":                  chat_id,
        "text":                     text,
        "parse_mode":               parse_mode,
        "disable_web_page_preview": disable_preview,
    })


def test_connection(token: str, chat_id: str) -> tuple[bool, str]:
    """Bağlantı testi için basit mesaj gönder."""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    msg = (
        "🤖 <b>AusbildungBot — Bağlantı Testi</b>\n\n"
        f"✅ Telegram entegrasyonu başarıyla çalışıyor!\n"
        f"📅 {now}"
    )
    return send_message(token, chat_id, msg)


def build_application_message(
    title: str,
    company: str,
    location: str,
    url: str,
    lang: str = "tr",
) -> str:
    """Başvuru bildirimi için Telegram HTML mesajı oluştur."""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    labels = {
        "tr": {
            "header":   "🎓 Ausbildung Başvurusu Yapıldı!",
            "position": "📌 <b>Pozisyon:</b>",
            "company":  "🏢 <b>Şirket:</b>",
            "location": "📍 <b>Konum:</b>",
            "link":     "🔗 İlana Git",
            "footer":   "🤖 AusbildungBot tarafından gönderildi",
        },
        "de": {
            "header":   "🎓 Ausbildungsbewerbung erfolgreich!",
            "position": "📌 <b>Position:</b>",
            "company":  "🏢 <b>Unternehmen:</b>",
            "location": "📍 <b>Ort:</b>",
            "link":     "🔗 Zur Stelle",
            "footer":   "🤖 Gesendet von AusbildungBot",
        },
        "en": {
            "header":   "🎓 Ausbildung Application Submitted!",
            "position": "📌 <b>Position:</b>",
            "company":  "🏢 <b>Company:</b>",
            "location": "📍 <b>Location:</b>",
            "link":     "🔗 View Listing",
            "footer":   "🤖 Sent by AusbildungBot",
        },
    }
    lb = labels.get(lang, labels["tr"])

    lines = [
        f"<b>{lb['header']}</b>",
        "",
        f"{lb['position']} {title}",
        f"{lb['company']} {company}",
        f"{lb['location']} {location}",
    ]
    if url:
        lines.append(f"\n{lb['link']}: {url}")
    lines += ["", f"📅 {now}", lb["footer"]]

    return "\n".join(lines)
