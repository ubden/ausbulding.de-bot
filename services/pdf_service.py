import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Windows sistem fontunu kaydet (Almanca ü/ö/ä/ß desteği için)
_FONT_REGISTERED = False

def _ensure_font():
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
    return "Helvetica"   # fallback (sınırlı karakter desteği)


def generate_anschreiben_pdf(
    anschreiben_text: str,
    job_title: str,
    company: str,
    user_info: dict,
) -> str:
    """
    Alman iş başvurusu formatında PDF üret.
    Döndürdüğü path geçici dosya — kullanıldıktan sonra silinmeli.

    user_info keys: vorname, nachname, strasse, plz, stadt, email
    """
    font = _ensure_font()

    vorname  = user_info.get("vorname", "")
    nachname = user_info.get("nachname", "")
    strasse  = user_info.get("strasse", "")
    plz      = user_info.get("plz", "")
    stadt    = user_info.get("stadt", "")
    email    = user_info.get("email", "")
    full_name = f"{vorname} {nachname}".strip()

    datum = datetime.now().strftime("%d.%m.%Y")

    # Geçici dosya
    tmp = tempfile.NamedTemporaryFile(
        suffix=".pdf", prefix="anschreiben_", delete=False
    )
    tmp.close()
    out_path = tmp.name

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    # ── Stiller ───────────────────────────────────────────────────
    normal = ParagraphStyle(
        "normal",
        fontName=font, fontSize=11, leading=16, alignment=TA_LEFT,
    )
    small = ParagraphStyle(
        "small",
        fontName=font, fontSize=9, leading=13, alignment=TA_LEFT, textColor=(0.3, 0.3, 0.3),
    )
    right = ParagraphStyle(
        "right",
        fontName=font, fontSize=11, leading=16, alignment=TA_RIGHT,
    )
    bold_style = ParagraphStyle(
        "bold",
        fontName=font, fontSize=11, leading=16, alignment=TA_LEFT,
    )
    subject_style = ParagraphStyle(
        "subject",
        fontName=font, fontSize=12, leading=18, alignment=TA_LEFT,
        spaceAfter=6,
    )

    story = []

    # ── Gönderici (sol üst) + Tarih (sağ üst) ────────────────────
    # Gönderici
    story.append(Paragraph(f"<b>{full_name}</b>", normal))
    if strasse:
        story.append(Paragraph(strasse, normal))
    if plz or stadt:
        story.append(Paragraph(f"{plz} {stadt}".strip(), normal))
    if email:
        story.append(Paragraph(email, small))

    story.append(Spacer(1, 0.4 * cm))

    # Tarih sağa
    story.append(Paragraph(f"{stadt or 'Stadt'}, {datum}", right))
    story.append(Spacer(1, 0.8 * cm))

    # ── Alıcı ────────────────────────────────────────────────────
    if company:
        story.append(Paragraph(f"<b>{company}</b>", normal))
    story.append(Spacer(1, 0.8 * cm))

    # ── Konu ─────────────────────────────────────────────────────
    betreff = f"Bewerbung als: {job_title}" if job_title else "Bewerbung"
    story.append(Paragraph(f"<b>{betreff}</b>", subject_style))
    story.append(Spacer(1, 0.4 * cm))

    # ── Anschreiben metni ─────────────────────────────────────────
    # Paragrafları ayır
    paragraphs = [p.strip() for p in anschreiben_text.split("\n") if p.strip()]
    for p in paragraphs:
        # HTML özel karakterlerini escape et
        p_safe = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(p_safe, normal))
        story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 0.8 * cm))

    # ── İmza ─────────────────────────────────────────────────────
    story.append(Paragraph("Mit freundlichen Grüßen,", normal))
    story.append(Spacer(1, 1.2 * cm))   # imza için boşluk
    story.append(Paragraph(f"<b>{full_name}</b>", normal))

    doc.build(story)
    return out_path
