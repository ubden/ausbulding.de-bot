import os
import re
import sys
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ── Font ────────────────────────────────────────────────────────────
_FONT_REGISTERED = False

def _ensure_font() -> str:
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return "Arial"
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\verdana.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            name = os.path.splitext(os.path.basename(path))[0].capitalize()
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                _FONT_REGISTERED = True
                return name
            except Exception:
                continue
    return "Helvetica"


# ── Paths ────────────────────────────────────────────────────────────

def _base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_anschreiben_dir() -> str:
    """Tüm Anschreiben PDF'lerinin saklandığı kök klasör."""
    d = os.path.join(_base_dir(), "anschreibens")
    os.makedirs(d, exist_ok=True)
    return d


def _safe_id(job_id: str) -> str:
    """Dosya sisteminde güvenli klasör ismi üret."""
    return re.sub(r"[^\w\-]", "_", job_id)[:60]


def get_anschreiben_path(job_id: str) -> str:
    """Belirli bir iş için PDF dosyasının tam yolunu döndür (dosya henüz olmayabilir)."""
    folder = os.path.join(get_anschreiben_dir(), _safe_id(job_id))
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "Anschreiben.pdf")


# ── Generator ────────────────────────────────────────────────────────

def generate_anschreiben_pdf(
    anschreiben_text: str,
    job_title: str,
    company: str,
    user_info: dict,
    job_id: str | None = None,
) -> str:
    """
    Alman başvuru formatında PDF üret.

    • job_id verilirse: anschreibens/<job_id>/Anschreiben.pdf olarak kaydeder.
      Aynı job_id için daha önce üretilmişse mevcut dosyayı döndürür (idempotent).
    • job_id verilmezse: geçici dosya kullanılır (eski davranış).

    Döndürdüğü string: oluşturulan veya mevcut PDF'in tam yolu.
    """
    if job_id:
        out_path = get_anschreiben_path(job_id)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            return out_path   # zaten mevcut — yeniden üretme
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", prefix="anschreiben_", delete=False)
        tmp.close()
        out_path = tmp.name

    _write_pdf(out_path, anschreiben_text, job_title, company, user_info)
    return out_path


def _write_pdf(
    out_path: str,
    anschreiben_text: str,
    job_title: str,
    company: str,
    user_info: dict,
) -> None:
    """PDF içeriğini out_path'e yaz."""
    font = _ensure_font()

    vorname  = user_info.get("vorname", "")
    nachname = user_info.get("nachname", "")
    strasse  = user_info.get("strasse", "")
    plz      = user_info.get("plz", "")
    stadt    = user_info.get("stadt", "")
    email    = user_info.get("email", "")
    full_name = f"{vorname} {nachname}".strip()
    datum     = datetime.now().strftime("%d.%m.%Y")

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    normal = ParagraphStyle("normal", fontName=font, fontSize=11, leading=16, alignment=TA_LEFT)
    small  = ParagraphStyle("small",  fontName=font, fontSize=9,  leading=13, alignment=TA_LEFT, textColor=(0.3, 0.3, 0.3))
    right  = ParagraphStyle("right",  fontName=font, fontSize=11, leading=16, alignment=TA_RIGHT)
    subj   = ParagraphStyle("subj",   fontName=font, fontSize=12, leading=18, alignment=TA_LEFT, spaceAfter=6)

    story = []

    # Gönderici
    story.append(Paragraph(f"<b>{full_name}</b>", normal))
    if strasse:
        story.append(Paragraph(strasse, normal))
    if plz or stadt:
        story.append(Paragraph(f"{plz} {stadt}".strip(), normal))
    if email:
        story.append(Paragraph(email, small))
    story.append(Spacer(1, 0.4 * cm))

    # Tarih
    story.append(Paragraph(f"{stadt or 'Stadt'}, {datum}", right))
    story.append(Spacer(1, 0.8 * cm))

    # Alıcı
    if company:
        story.append(Paragraph(f"<b>{company}</b>", normal))
    story.append(Spacer(1, 0.8 * cm))

    # Konu
    betreff = f"Bewerbung als: {job_title}" if job_title else "Bewerbung"
    story.append(Paragraph(f"<b>{betreff}</b>", subj))
    story.append(Spacer(1, 0.4 * cm))

    # Metin
    for p in [p.strip() for p in anschreiben_text.split("\n") if p.strip()]:
        p_safe = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(p_safe, normal))
        story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("Mit freundlichen Grüßen,", normal))
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(f"<b>{full_name}</b>", normal))

    doc.build(story)
