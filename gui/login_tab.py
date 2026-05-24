import webbrowser
import customtkinter as ctk
from utils.config import load_config, save_config
from utils.i18n import t

PROFILE_URL = "https://www.ausbildung.de/dashboard/azubi/profil/#tab-bar-anchor"


class LoginTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._cfg = load_config()
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        mid = ctk.CTkFrame(scroll, fg_color="transparent")
        mid.grid(row=0, column=0, pady=30)
        mid.grid_columnconfigure(0, weight=1)

        # ── Giriş kartı ──────────────────────────────────────────
        card = ctk.CTkFrame(mid, corner_radius=16, border_width=1, border_color=("gray75", "gray32"))
        card.grid(row=0, column=0, padx=60, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        hdr = ctk.CTkFrame(card, fg_color=("#5b2d8e", "#3d1f63"), corner_radius=12)
        hdr.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="ew")
        ctk.CTkLabel(
            hdr, text=t("LOGIN_HEADER"),
            font=ctk.CTkFont(size=16, weight="bold"), text_color="white",
        ).grid(row=0, column=0, padx=24, pady=14, sticky="w")

        ctk.CTkLabel(card, text=t("LOGIN_EMAIL"), font=ctk.CTkFont(size=13)).grid(
            row=1, column=0, padx=(28, 8), pady=(20, 8), sticky="e")
        self._email_var = ctk.StringVar(value=self._cfg.get("email", ""))
        self._email_entry = ctk.CTkEntry(
            card, textvariable=self._email_var, width=360, height=38,
            placeholder_text=t("LOGIN_EMAIL_PH"), font=ctk.CTkFont(size=13),
        )
        self._email_entry.grid(row=1, column=1, padx=(0, 28), pady=(20, 8), sticky="w")

        ctk.CTkLabel(card, text=t("LOGIN_PASSWORD"), font=ctk.CTkFont(size=13)).grid(
            row=2, column=0, padx=(28, 8), pady=8, sticky="e")
        self._pass_var = ctk.StringVar(value=self._cfg.get("password", ""))
        self._pass_entry = ctk.CTkEntry(
            card, textvariable=self._pass_var, width=360, height=38, show="*",
            placeholder_text=t("LOGIN_PASS_PH"), font=ctk.CTkFont(size=13),
        )
        self._pass_entry.grid(row=2, column=1, padx=(0, 28), pady=8, sticky="w")

        self._show_pass = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            card, text=t("LOGIN_SHOW_PASS"),
            variable=self._show_pass, command=self._toggle_pass,
        ).grid(row=3, column=1, padx=(0, 28), pady=(2, 6), sticky="w")

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=4, column=0, columnspan=2, padx=28, pady=(8, 24), sticky="ew")
        btn_row.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(btn_row, text=t("LOGIN_SAVE"), width=150, height=36, command=self._save).grid(row=0, column=0)
        self._status_label = ctk.CTkLabel(btn_row, text="", text_color="#2ecc71", font=ctk.CTkFont(size=12))
        self._status_label.grid(row=0, column=1, padx=(16, 0), sticky="w")

        ctk.CTkLabel(mid, text=t("LOGIN_INFO"), font=ctk.CTkFont(size=10), text_color="gray").grid(
            row=1, column=0, pady=(8, 16))

        # ── Önemli Not ───────────────────────────────────────────
        note = ctk.CTkFrame(
            mid, corner_radius=14,
            fg_color=("#fff8e6", "#2e2200"),
            border_width=1, border_color=("#f0a500", "#a07000"),
        )
        note.grid(row=2, column=0, padx=60, pady=(0, 16), sticky="ew")
        note.grid_columnconfigure(0, weight=1)

        note_hdr = ctk.CTkFrame(note, fg_color=("#f0a500", "#7a5800"), corner_radius=10)
        note_hdr.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        ctk.CTkLabel(
            note_hdr, text=t("LOGIN_NOTE_TITLE"),
            font=ctk.CTkFont(size=13, weight="bold"), text_color="white",
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(
            note, text=t("LOGIN_NOTE_BODY"),
            font=ctk.CTkFont(size=12),
            text_color=("#5a3a00", "#e8c87a"),
            justify="left", anchor="w",
        ).grid(row=1, column=0, padx=24, pady=(14, 10), sticky="w")

        link_frame = ctk.CTkFrame(note, fg_color=("white", "#1a1000"), corner_radius=8)
        link_frame.grid(row=2, column=0, padx=24, pady=(0, 20), sticky="w")
        link_lbl = ctk.CTkLabel(
            link_frame, text=t("LOGIN_PROFILE_LINK"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1a5fa8", "#4da3ff"), cursor="hand2",
        )
        link_lbl.pack(padx=8, pady=8)
        link_lbl.bind("<Button-1>", lambda _e: webbrowser.open(PROFILE_URL))
        link_frame.bind("<Button-1>", lambda _e: webbrowser.open(PROFILE_URL))

    def _toggle_pass(self):
        self._pass_entry.configure(show="" if self._show_pass.get() else "*")

    def _save(self):
        cfg = load_config()
        cfg["email"]    = self._email_var.get().strip()
        cfg["password"] = self._pass_var.get()
        save_config(cfg)
        self._status_label.configure(text=t("LOGIN_SAVED"), text_color="#2ecc71")
        self.after(2500, lambda: self._status_label.configure(text=""))

    def get_credentials(self) -> tuple[str, str]:
        return self._email_var.get().strip(), self._pass_var.get()
