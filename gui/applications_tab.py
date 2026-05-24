import webbrowser
import customtkinter as ctk
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

# (i18n key, width, anchor) — headers resolved at runtime via t()
_COL_DEFS = [
    ("APPS_COL_IDX",      38,  "center"),
    ("APPS_COL_POSITION", 260, "w"),
    ("APPS_COL_COMPANY",  165, "w"),
    ("APPS_COL_LOCATION", 130, "w"),
    ("APPS_COL_STATUS",   150, "center"),
    ("APPS_COL_DATE",     115, "w"),
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
            ctk.CTkLabel(
                card, text=_STAT_ICONS[key], font=ctk.CTkFont(size=20),
            ).pack(pady=(10, 2))
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
        url = app.get("url", "") or ""
        cols = _columns()
        status_short = _status_short()

        def _open(_e=None):
            if url:
                webbrowser.open(url)

        title    = _trunc(app.get("title") or "",    50)
        company  = _trunc(app.get("company") or "",  28)
        location = _trunc(app.get("location") or "", 20)
        status   = app.get("status") or "pending"
        date_raw = app.get("applied_at") or app.get("created_at") or ""
        date_str = date_raw[:16]

        _label(parent, str(idx),  cols[0][1], "center", bold=False, click=_open, col=0)
        _label(parent, title,     cols[1][1], "w",      bold=False, click=_open, col=1)
        _label(parent, company,   cols[2][1], "w",      bold=False, click=_open, col=2)
        _label(parent, location,  cols[3][1], "w",      bold=False, click=_open, col=3)

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
            text=status_short.get(status, status),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
        )
        pill_lbl.pack(padx=10, pady=4)
        pill.bind("<Button-1>", _open)
        pill_lbl.bind("<Button-1>", _open)

        _label(parent, date_str, cols[5][1], "w", bold=False, click=_open, col=5)

        # Error row
        err = (app.get("error_message") or "").strip()
        if err and status == "error":
            err_lbl = ctk.CTkLabel(
                parent,
                text=f"  ⚠ {_trunc(err, 120)}",
                font=ctk.CTkFont(size=10),
                text_color="#e74c3c",
                anchor="w",
            )
            err_lbl.grid(row=1, column=1, columnspan=5, padx=(6, 6), pady=(0, 4), sticky="w")
            err_lbl.bind("<Button-1>", _open)

    def add_job(self, job: dict):
        self.after(0, self.refresh)

    def _clear_db(self):
        import tkinter.messagebox as mb
        if mb.askyesno(t("APPS_CONFIRM_TITLE"), t("APPS_CONFIRM_MSG")):
            count = clear_all()
            self.refresh()
            mb.showinfo(t("APPS_CLEARED_TITLE"), f"{count} {t('APPS_CLEARED_MSG')}")


# ── Helpers ───────────────────────────────────────────────────────────

def _trunc(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n - 1] + "…"


def _label(parent, text, width, anchor, bold, click, col):
    lbl = ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(size=12, weight="bold" if bold else "normal"),
        width=width, anchor=anchor,
    )
    lbl.grid(row=0, column=col, padx=(6, 2), pady=7, sticky="w")
    if click:
        lbl.bind("<Button-1>", click)
