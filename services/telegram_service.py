"""
Telegram Bot API — mesaj gönderme servisi.
Harici bağımlılık yok: sadece stdlib urllib kullanılır.
"""

import json
import os
import ssl
import urllib.request
import urllib.error
from datetime import datetime
from html import escape


_BASE = "https://api.telegram.org/bot{token}/{method}"


def _ssl_context():
    """
    Windows sunucularda PyInstaller/OpenSSL bazen sistem sertifika deposunu görmez.
    truststore varsa OS sertifika deposunu, yoksa certifi CA bundle'ını kullan.
    """
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        pass

    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _format_network_error(err: Exception) -> str:
    text = str(err)
    reason = getattr(err, "reason", None)
    reason_text = str(reason) if reason is not None else text
    if isinstance(reason, ssl.SSLCertVerificationError) or "CERTIFICATE_VERIFY_FAILED" in reason_text:
        return (
            "SSL sertifika doğrulaması başarısız. Server'da HTTPS trafiğini "
            "denetleyen proxy/antivirüs self-signed sertifika kullanıyor olabilir. "
            "Proxy/root sertifikasını Windows Trusted Root'a yükleyin veya sistem "
            "yöneticinizden api.telegram.org için geçerli sertifika zinciri isteyin. "
            f"Detay: {reason_text[:180]}"
        )
    return text


def _post(token: str, method: str, payload: dict, timeout: int = 10) -> tuple[bool, str]:
    url  = _BASE.format(token=token, method=method)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req  = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()):
            return True, ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            msg = json.loads(body).get("description", body[:200])
        except Exception:
            msg = body[:200]
        return False, msg
    except urllib.error.URLError as e:
        return False, _format_network_error(e)
    except Exception as e:
        return False, _format_network_error(e)


def _post_multipart(
    token: str,
    method: str,
    fields: dict,
    file_field: str,
    file_path: str,
    timeout: int = 20,
) -> tuple[bool, str]:
    url = _BASE.format(token=token, method=method)
    boundary = f"----AusbildungBot{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    body = bytearray()

    def _add_field(name: str, value: str):
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for key, value in fields.items():
        if value is not None:
            _add_field(key, value)

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode("utf-8")
    )
    body.extend(b"Content-Type: application/pdf\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()):
            return True, ""
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8", errors="replace")
        try:
            msg = json.loads(resp_body).get("description", resp_body[:200])
        except Exception:
            msg = resp_body[:200]
        return False, msg
    except urllib.error.URLError as e:
        return False, _format_network_error(e)
    except Exception as e:
        return False, _format_network_error(e)


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


def send_document(
    token: str,
    chat_id: str,
    file_path: str,
    caption: str = "",
    parse_mode: str = "HTML",
) -> tuple[bool, str]:
    """Telegram'a PDF doküman gönder."""
    if not token or not chat_id:
        return False, "Token veya Chat ID eksik"
    if not file_path or not os.path.isfile(file_path):
        return False, "PDF dosyası bulunamadı"
    return _post_multipart(
        token,
        "sendDocument",
        {
            "chat_id": chat_id,
            "caption": caption[:1024],
            "parse_mode": parse_mode if caption else None,
        },
        "document",
        file_path,
    )


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
    cover_letter: str = "",
) -> str:
    """Başvuru bildirimi için Telegram HTML mesajı oluştur."""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    labels = {
        "tr": {
            "header":   "🎓 Ausbildung Başvurusu Yapıldı!",
            "position": "📌 <b>Meslek/Pozisyon:</b>",
            "company":  "🏢 <b>Şirket:</b>",
            "location": "📍 <b>Konum:</b>",
            "cover":    "✍️ <b>Kurz-Anschreiben:</b>",
            "link":     "🔗 İlana Git",
            "footer":   "🤖 AusbildungBot tarafından gönderildi",
        },
        "de": {
            "header":   "🎓 Ausbildungsbewerbung erfolgreich!",
            "position": "📌 <b>Beruf/Position:</b>",
            "company":  "🏢 <b>Unternehmen:</b>",
            "location": "📍 <b>Ort:</b>",
            "cover":    "✍️ <b>Kurz-Anschreiben:</b>",
            "link":     "🔗 Zur Stelle",
            "footer":   "🤖 Gesendet von AusbildungBot",
        },
        "en": {
            "header":   "🎓 Ausbildung Application Submitted!",
            "position": "📌 <b>Profession/Position:</b>",
            "company":  "🏢 <b>Company:</b>",
            "location": "📍 <b>Location:</b>",
            "cover":    "✍️ <b>Short cover letter:</b>",
            "link":     "🔗 View Listing",
            "footer":   "🤖 Sent by AusbildungBot",
        },
    }
    lb = labels.get(lang, labels["tr"])
    safe_title    = escape(title or "-")
    safe_company  = escape(company or "-")
    safe_location = escape(location or "-")
    safe_url      = escape(url or "", quote=True)
    safe_cover    = escape((cover_letter or "").strip())

    lines = [
        f"<b>{lb['header']}</b>",
        "",
        f"{lb['position']} {safe_title}",
        f"{lb['company']} {safe_company}",
        f"{lb['location']} {safe_location}",
    ]
    if safe_cover:
        lines += ["", f"{lb['cover']}\n{safe_cover[:2800]}"]
    if safe_url:
        lines.append(f'\n<a href="{safe_url}">{lb["link"]}</a>')
    lines += ["", f"📅 {now}", lb["footer"]]

    return "\n".join(lines)
