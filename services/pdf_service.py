import os
import re
import sys
import tempfile
from datetime import datetime
from html import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ── Font ────────────────────────────────────────────────────────────
_FONT_REGISTERED = False
_FONT_NAME = "AusbildungSans"


def _ensure_font() -> str:
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return _FONT_NAME
    candidates = [
        (
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\ariali.ttf",
            r"C:\Windows\Fonts\arialbi.ttf",
        ),
        (
            r"C:\Windows\Fonts\calibri.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
            r"C:\Windows\Fonts\calibrii.ttf",
            r"C:\Windows\Fonts\calibriz.ttf",
        ),
        (
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\segoeuii.ttf",
            r"C:\Windows\Fonts\segoeuiz.ttf",
        ),
        (
            r"C:\Windows\Fonts\verdana.ttf",
            r"C:\Windows\Fonts\verdanab.ttf",
            r"C:\Windows\Fonts\verdanai.ttf",
            r"C:\Windows\Fonts\verdanaz.ttf",
        ),
    ]
    for normal_path, bold_path, italic_path, bold_italic_path in candidates:
        if os.path.exists(normal_path):
            try:
                pdfmetrics.registerFont(TTFont(_FONT_NAME, normal_path))
                pdfmetrics.registerFont(TTFont(f"{_FONT_NAME}-Bold", bold_path if os.path.exists(bold_path) else normal_path))
                pdfmetrics.registerFont(TTFont(f"{_FONT_NAME}-Italic", italic_path if os.path.exists(italic_path) else normal_path))
                pdfmetrics.registerFont(TTFont(f"{_FONT_NAME}-BoldItalic", bold_italic_path if os.path.exists(bold_italic_path) else normal_path))
                pdfmetrics.registerFontFamily(
                    _FONT_NAME,
                    normal=_FONT_NAME,
                    bold=f"{_FONT_NAME}-Bold",
                    italic=f"{_FONT_NAME}-Italic",
                    boldItalic=f"{_FONT_NAME}-BoldItalic",
                )
                _FONT_REGISTERED = True
                return _FONT_NAME
            except Exception:
                continue
    return "Helvetica"


def _normalize_german_chars(text: str) -> str:
    """Common ASCII transliterations from LLM output into proper German spelling."""
    if not text:
        return ""
    replacements = {
        r"strasse\b": "straße",
        r"Strasse\b": "Straße",
        r"\bfuer\b": "für",
        r"\bFuer\b": "Für",
        r"\bueber\b": "über",
        r"\bUeber\b": "Über",
        r"\bmoechte\b": "möchte",
        r"\bMoechte\b": "Möchte",
        r"\bmoechten\b": "möchten",
        r"\bMoechten\b": "Möchten",
        r"\bkoennte\b": "könnte",
        r"\bKoennte\b": "Könnte",
        r"\bkoennen\b": "können",
        r"\bKoennen\b": "Können",
        r"\bwuerde\b": "würde",
        r"\bWuerde\b": "Würde",
        r"\bwaere\b": "wäre",
        r"\bWaere\b": "Wäre",
        r"\bgroesse\b": "größe",
        r"\bGroesse\b": "Größe",
        r"\bgrossen\b": "großen",
        r"\bGrossen\b": "Großen",
        r"\bgrosses\b": "großes",
        r"\bGrosses\b": "Großes",
        r"\bgross\b": "groß",
        r"\bGross\b": "Groß",
        r"\bGruesse\b": "Grüße",
        r"\bGruessen\b": "Grüßen",
        r"\bgruessen\b": "grüßen",
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)
    return text


def _xml(text: str) -> str:
    return escape(_normalize_german_chars(str(text or "")), quote=False)


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
      Dosya varsa güncel font/karakter ayarlarıyla yeniden yazar.
    • job_id verilmezse: geçici dosya kullanılır (eski davranış).

    Döndürdüğü string: oluşturulan veya mevcut PDF'in tam yolu.
    """
    if job_id:
        out_path = get_anschreiben_path(job_id)
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
    anschreiben_text = _normalize_german_chars(anschreiben_text)
    job_title = _normalize_german_chars(job_title)
    company = _normalize_german_chars(company)

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
    story.append(Paragraph(f"<b>{_xml(full_name)}</b>", normal))
    if strasse:
        story.append(Paragraph(_xml(strasse), normal))
    if plz or stadt:
        story.append(Paragraph(_xml(f"{plz} {stadt}".strip()), normal))
    if email:
        story.append(Paragraph(_xml(email), small))
    story.append(Spacer(1, 0.4 * cm))

    # Tarih
    story.append(Paragraph(_xml(f"{stadt or 'Stadt'}, {datum}"), right))
    story.append(Spacer(1, 0.8 * cm))

    # Alıcı
    if company:
        story.append(Paragraph(f"<b>{_xml(company)}</b>", normal))
    story.append(Spacer(1, 0.8 * cm))

    # Konu
    betreff = f"Bewerbung als: {job_title}" if job_title else "Bewerbung"
    story.append(Paragraph(f"<b>{_xml(betreff)}</b>", subj))
    story.append(Spacer(1, 0.4 * cm))

    # Metin
    for p in [p.strip() for p in anschreiben_text.split("\n") if p.strip()]:
        story.append(Paragraph(_xml(p), normal))
        story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("Mit freundlichen Grüßen,", normal))
    story.append(Spacer(1, 1.2 * cm))
    story.append(Paragraph(f"<b>{_xml(full_name)}</b>", normal))

    doc.build(story)
