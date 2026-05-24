import io
import os
import webbrowser
import customtkinter as ctk
from PIL import Image
from services.database import get_all_applications, get_stats, clear_all
from utils.i18n import t

STATUS_COLORS = {
    "applied":         "#1a9b4f",
    "already_applied": "#8e44ad",
    "skipped":         "#e67e22",
    "error":           "#c0392b",
    "pending":         "#7f8c8d",
}
STATUS_TINTS = {
    "applied":         ("#d5f0e2", "#0e2d1a"),
    "already_applied": ("#e8d5f5", "#2a1040"),
    "skipped":         ("#fce8d0", "#3d2000"),
    "error":           ("#f5d0ce", "#3d0e0c"),
}
_STAT_KEYS = {
    "applied":         "APPS_S_APPLIED",
    "already_applied": "APPS_S_ALREADY",
    "skipped":         "APPS_S_SKIPPED",
    "error":           "APPS_S_ERROR",
    "pending":         "APPS_S_PENDING",
}
_STAT_ICONS = {
    "applied": "✅", "already_applied": "🔁", "skipped": "⏭", "error": "❌",
}

# Column defs — (i18n key, width, anchor)
_COL_DEFS = [
    ("APPS_COL_IDX",      38,  "center"),
    ("APPS_COL_POSITION", 245, "w"),
    ("APPS_COL_COMPANY",  155, "w"),
    ("APPS_COL_LOCATION", 120, "w"),
    ("APPS_COL_STATUS",   145, "center"),
    ("APPS_COL_DATE",     110, "w"),
    ("APPS_COL_PDF",       46, "center"),   # PDF preview button column
]


def _columns():
    return [(t(key), width, anchor) for key, width, anchor in _COL_DEFS]


def _status_short() -> dict:
    return {k: t(v) for k, v in _STAT_KEYS.items()}


class ApplicationsTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build()
        self.refresh()

    # ── Layout ────────────────────────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ── Başlık kartı ─────────────────────────────────────────────
        top_card = ctk.CTkFrame(self, corner_radius=12, border_width=1, border_color=("gray78", "gray30"))
        top_card.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")
        top_card.grid_columnconfigure(0, weight=1)

        top_hdr = ctk.CTkFrame(top_card, fg_color=("#5b2d8e", "#3d1f63"), corner_radius=10)
        top_hdr.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        top_hdr.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            top_hdr, text=t("APPS_HEADER"),
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white",
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        btn_frame = ctk.CTkFrame(top_hdr, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=12, pady=8, sticky="e")
        ctk.CTkButton(
            btn_frame, text=t("APPS_REFRESH"), width=110, height=32,
            fg_color=("gray60", "gray40"), hover_color=("gray45", "gray28"),
            command=self.refresh,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btn_frame, text=t("APPS_CLEAR_DB"), width=130, height=32,
            fg_color="#c0392b", hover_color="#922b21",
            command=self._clear_db,
        ).pack(side="left")

        # ── İstatistik kartları ───────────────────────────────────────
        stats_row = ctk.CTkFrame(top_card, fg_color="transparent")
        stats_row.grid(row=1, column=0, padx=14, pady=(12, 14), sticky="ew")
        stats_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._stat_labels: dict[str, ctk.CTkLabel] = {}

        for i, key in enumerate(["applied", "already_applied", "skipped", "error"]):
            card = ctk.CTkFrame(
                stats_row,
                fg_color=STATUS_TINTS[key],
                corner_radius=10,
                border_width=1,
                border_color=STATUS_COLORS[key],
            )
            card.grid(row=0, column=i, padx=5, pady=0, sticky="ew")
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(card, text=_STAT_ICONS[key], font=ctk.CTkFont(size=20)).pack(pady=(10, 2))
            lbl = ctk.CTkLabel(
                card, text="",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=STATUS_COLORS[key],
            )
            lbl.pack(pady=(0, 10))
            self._stat_labels[key] = lbl

        # ── Sütun başlıkları ─────────────────────────────────────────
        self._col_header = ctk.CTkFrame(self, fg_color=("gray82", "gray26"), corner_radius=8)
        self._col_header.grid(row=2, column=0, padx=16, pady=(0, 2), sticky="ew")
        self._fill_header(self._col_header)

        # ── Satır listesi ─────────────────────────────────────────────
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray96", "gray14"),
            corner_radius=8,
            border_width=1,
            border_color=("gray78", "gray30"),
        )
        self._scroll.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="nsew")
        self._scroll.grid_columnconfigure(0, weight=1)

    def _fill_header(self, parent):
        for col_i, (text, width, anchor) in enumerate(_columns()):
            ctk.CTkLabel(
                parent, text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width, anchor=anchor,
            ).grid(row=0, column=col_i, padx=(6, 2), pady=8, sticky="w")

    # ── Data ──────────────────────────────────────────────────────────

    def refresh(self):
        stats = get_stats()
        for key, lbl in self._stat_labels.items():
            lbl.configure(text=f"{t(_STAT_KEYS[key])}\n{stats.get(key, 0)}")

        for w in self._scroll.winfo_children():
            w.destroy()

        apps = get_all_applications()
        if not apps:
            ctk.CTkLabel(
                self._scroll,
                text=t("APPS_EMPTY"),
                text_color="gray",
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, padx=20, pady=50)
            return

        for i, app in enumerate(apps):
            bg = ("gray92", "gray17") if i % 2 == 0 else ("white", "gray21")
            row_frame = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=5)
            row_frame.grid(row=i, column=0, padx=4, pady=1, sticky="ew")
            self._scroll.grid_columnconfigure(0, weight=1)
            self._fill_row(row_frame, i + 1, app)

    def _fill_row(self, parent: ctk.CTkFrame, idx: int, app: dict):
        url     = app.get("url", "") or ""
        cols    = _columns()
        ss      = _status_short()
        pdf_p   = app.get("pdf_path") or ""
        has_pdf = bool(pdf_p and os.path.isfile(pdf_p))

        def _open(_e=None):
            if url:
                webbrowser.open(url)

        title    = _trunc(app.get("title") or "",    46)
        company  = _trunc(app.get("company") or "",  26)
        location = _trunc(app.get("location") or "", 18)
        status   = app.get("status") or "pending"
        date_raw = app.get("applied_at") or app.get("created_at") or ""
        date_str = date_raw[:16]

        _label(parent, str(idx),  cols[0][1], "center", click=_open, col=0)
        _label(parent, title,     cols[1][1], "w",      click=_open, col=1)
        _label(parent, company,   cols[2][1], "w",      click=_open, col=2)
        _label(parent, location,  cols[3][1], "w",      click=_open, col=3)

        # Status pill
        pill = ctk.CTkFrame(
            parent,
            fg_color=STATUS_COLORS.get(status, "#7f8c8d"),
            corner_radius=10,
            width=cols[4][1] - 10,
        )
        pill.grid(row=0, column=4, padx=4, pady=5)
        pill_lbl = ctk.CTkLabel(
            pill,
            text=ss.get(status, status),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
        )
        pill_lbl.pack(padx=10, pady=4)
        pill.bind("<Button-1>", _open)
        pill_lbl.bind("<Button-1>", _open)

        _label(parent, date_str, cols[5][1], "w", click=_open, col=5)

        # PDF preview button
        if has_pdf:
            label_text = f"{t('APPS_COL_PDF')[:30]} @ {app.get('company','')[:20]}"
            ctk.CTkButton(
                parent,
                text="📄",
                width=cols[6][1] - 4,
                height=26,
                fg_color="#6c3483",
                hover_color="#5b2d6e",
                font=ctk.CTkFont(size=14),
                command=lambda p=pdf_p, lbl=label_text: PDFPreviewModal(self, p, lbl),
            ).grid(row=0, column=6, padx=(2, 6), pady=5)
        else:
            ctk.CTkLabel(parent, text="", width=cols[6][1]).grid(row=0, column=6, padx=(2, 6))

        # Error sub-row
        err = (app.get("error_message") or "").strip()
        if err and status == "error":
            err_lbl = ctk.CTkLabel(
                parent,
                text=f"  ⚠ {_trunc(err, 110)}",
                font=ctk.CTkFont(size=10),
                text_color="#e74c3c",
                anchor="w",
            )
            err_lbl.grid(row=1, column=1, columnspan=6, padx=(6, 6), pady=(0, 4), sticky="w")
            err_lbl.bind("<Button-1>", _open)

    def add_job(self, job: dict):
        self.after(0, self.refresh)

    def _clear_db(self):
        import tkinter.messagebox as mb
        if mb.askyesno(t("APPS_CONFIRM_TITLE"), t("APPS_CONFIRM_MSG")):
            count = clear_all()
            self.refresh()
            mb.showinfo(t("APPS_CLEARED_TITLE"), f"{count} {t('APPS_CLEARED_MSG')}")


# ── PDF Önizleme Modalı ────────────────────────────────────────────────

class PDFPreviewModal(ctk.CTkToplevel):
    """
    Oluşturulmuş Anschreiben PDF'ini uygulama içinde önizle.
    PyMuPDF (fitz) kuruluysa sayfaları image olarak render eder;
    kurulu değilse sistem PDF görüntüleyicisini açmayı teklif eder.
    """

    _RENDER_DPI = 150   # render kalitesi (yükseltmek daha net ama daha yavaş)

    def __init__(self, master, pdf_path: str, label: str = ""):
        super().__init__(master)
        self.title(f"📄  {t('APPS_PDF_TITLE')}  —  {label[:60]}")
        self.geometry("700x920")
        self.minsize(520, 600)
        self.resizable(True, True)
        self.grab_set()
        self.focus_set()

        self._pdf_path = pdf_path
        self._ctk_images: list = []   # CTkImage referanslarını tut (GC'den koru)

        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Başlık çubuğu ───────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=("#5b2d8e", "#3d1f63"), corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            hdr,
            text=f"  📄  {t('APPS_PDF_TITLE')}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
        ).grid(row=0, column=0, padx=14, pady=10, sticky="w")

        btn_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=8, pady=6, sticky="e")

        ctk.CTkButton(
            btn_frame, text=t("APPS_PDF_OPEN_SYS"), width=140, height=30,
            fg_color="#1f6aa5", hover_color="#144d7a",
            font=ctk.CTkFont(size=11),
            command=self._open_system,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text=t("APPS_PDF_CLOSE"), width=80, height=30,
            fg_color="#c0392b", hover_color="#922b21",
            font=ctk.CTkFont(size=11),
            command=self.destroy,
        ).pack(side="left")

        # ── İçerik ──────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color=("gray80", "gray16"), corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        try:
            import fitz   # PyMuPDF
            self._render_with_fitz(scroll)
        except ImportError:
            self._render_fallback(scroll, no_fitz=True)
        except Exception as e:
            self._render_fallback(scroll, no_fitz=False, err=str(e))

    def _render_with_fitz(self, parent):
        doc = fitz.open(self._pdf_path)
        scale = self._RENDER_DPI / 72   # 72 DPI is fitz default
        mat   = fitz.Matrix(scale, scale)

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix  = page.get_pixmap(matrix=mat, alpha=False)
            img  = Image.open(io.BytesIO(pix.tobytes("png")))

            # CTkImage: display at 96 dpi equivalent (half of 150)
            display_w = int(img.width * 72 / self._RENDER_DPI)
            display_h = int(img.height * 72 / self._RENDER_DPI)
            ctk_img = ctk.CTkImage(
                light_image=img, dark_image=img,
                size=(display_w, display_h),
            )
            self._ctk_images.append(ctk_img)   # keep reference

            lbl = ctk.CTkLabel(
                parent, image=ctk_img, text="",
                fg_color=("gray95", "gray12"),
                corner_radius=4,
            )
            lbl.grid(row=page_num, column=0, padx=16, pady=(10 if page_num == 0 else 4, 4), sticky="n")

        doc.close()

    def _render_fallback(self, parent, no_fitz: bool, err: str = ""):
        row = 0
        if no_fitz:
            msg = t("APPS_PDF_NO_FITZ")
        else:
            msg = f"{t('APPS_PDF_LOAD_ERR')}\n{err}"
        ctk.CTkLabel(
            parent, text=msg,
            font=ctk.CTkFont(size=12), text_color=("gray30", "gray70"),
            justify="center",
        ).grid(row=row, column=0, padx=30, pady=(60, 16))
        row += 1
        ctk.CTkButton(
            parent, text=t("APPS_PDF_OPEN_BTN"), width=200, height=38,
            fg_color="#1f6aa5", hover_color="#144d7a",
            command=self._open_system,
        ).grid(row=row, column=0, pady=8)

    def _open_system(self):
        try:
            os.startfile(self._pdf_path)
        except Exception:
            webbrowser.open(self._pdf_path)


# ── Helpers ───────────────────────────────────────────────────────────

def _trunc(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n - 1] + "…"


def _label(parent, text, width, anchor, click, col):
    lbl = ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(size=12),
        width=width, anchor=anchor,
    )
    lbl.grid(row=0, column=col, padx=(6, 2), pady=7, sticky="w")
    if click:
        lbl.bind("<Button-1>", click)
