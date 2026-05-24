import threading
import customtkinter as ctk
from utils.config import load_config, save_config
from utils.i18n import t, get_lang, LANG_OPTIONS

RADIUS_OPTIONS = ["10", "25", "50", "100", "200"]
AUSBILDUNGSART_OPTIONS = ["", "Duale Ausbildung", "Duales Studium", "Schulische Ausbildung"]
ABSCHLUSS_OPTIONS = ["", "Hauptschulabschluss", "Mittlere Reife", "Fachabitur", "Abitur"]
BRANCHE_OPTIONS = [
    "",
    "Banken und Versicherungen",
    "Bau und Architektur",
    "Bildung und Erziehung",
    "Büro und Verwaltung",
    "Chemie und Pharma",
    "Dienstleistungen",
    "Elektrotechnik",
    "Energie und Umwelt",
    "Fahrzeuge und Maschinenbau",
    "Gastronomie und Tourismus",
    "Garten und Forstwirtschaft",
    "Gesundheit und Soziales",
    "Handel",
    "Handwerk",
    "Immobilien",
    "IT und Technik",
    "Landwirtschaft",
    "Logistik",
    "Medien und Journalismus",
    "Mode und Textil",
    "Öffentlicher Dienst",
    "Recht und Steuern",
    "Sport und Fitness",
    "Tourismus und Reisen",
]


class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._cfg = load_config()
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(1, weight=1)

        f   = scroll
        row = 0

        def _section(key: str, icon: str = ""):
            nonlocal row
            if row > 0:
                sep = ctk.CTkFrame(f, height=1, fg_color=("gray75", "gray35"))
                sep.grid(row=row, column=0, columnspan=2, padx=16, pady=(10, 0), sticky="ew")
                row += 1
            label = f"  {icon}  {t(key)}" if icon else f"  {t(key)}"
            ctk.CTkLabel(
                f, text=label,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#5b2d8e", "#caa8f0"), anchor="w",
            ).grid(row=row, column=0, columnspan=2, padx=16, pady=(10, 6), sticky="w")
            row += 1

        # ── Dil seçimi ────────────────────────────────────────────
        _section("SETTINGS_LANG_SECTION", "🌐")

        ctk.CTkLabel(f, text=t("LANG_LABEL")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        lang_frame = ctk.CTkFrame(f, fg_color="transparent")
        lang_frame.grid(row=row, column=1, padx=(0, 20), pady=6, sticky="w")

        cur = get_lang()
        for code, label in LANG_OPTIONS.items():
            btn = ctk.CTkButton(
                lang_frame, text=label,
                width=110, height=32,
                fg_color=("#5b2d8e", "#3d1f63") if code == cur else ("gray50", "gray35"),
                hover_color=("#4a2070", "#2e1248"),
                command=lambda c=code: self._change_lang(c),
            )
            btn.pack(side="left", padx=(0, 6))
        row += 1

        # ── OpenAI ───────────────────────────────────────────────
        _section("SETTINGS_OPENAI", "🤖")

        ctk.CTkLabel(f, text=t("SETTINGS_OPENAI_KEY")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._api_key_var = ctk.StringVar(value=self._cfg.get("openai_key", ""))
        self._api_key_entry = ctk.CTkEntry(f, textvariable=self._api_key_var, width=380, show="*", placeholder_text="sk-...")
        self._api_key_entry.grid(row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        ctk.CTkCheckBox(f, text=t("SETTINGS_SHOW_KEY"), command=self._toggle_key).grid(
            row=row, column=1, padx=(0, 20), pady=(0, 4), sticky="w"); row += 1

        ctk.CTkLabel(f, text=t("SETTINGS_OPENAI_BG"), anchor="ne").grid(row=row, column=0, padx=20, pady=6, sticky="ne")
        self._bg_text = ctk.CTkTextbox(f, width=380, height=80)
        self._bg_text.insert("1.0", self._cfg.get("user_background", ""))
        self._bg_text.grid(row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1
        ctk.CTkLabel(f, text=t("SETTINGS_OPENAI_BG_HINT"),
                     font=ctk.CTkFont(size=10), text_color="gray").grid(
            row=row, column=1, padx=(0, 20), sticky="w"); row += 1

        # ── Arama ────────────────────────────────────────────────
        _section("SETTINGS_SEARCH", "🔍")

        ctk.CTkLabel(f, text=t("SETTINGS_CITY")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._city_var = ctk.StringVar(value=self._cfg.get("city", "Heidelberg"))
        ctk.CTkEntry(f, textvariable=self._city_var, width=200, placeholder_text=t("SETTINGS_CITY_PH")).grid(
            row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        ctk.CTkLabel(f, text=t("SETTINGS_RADIUS")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._radius_var = ctk.StringVar(value=self._cfg.get("radius", "25"))
        ctk.CTkOptionMenu(f, values=RADIUS_OPTIONS, variable=self._radius_var, width=120).grid(
            row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        # ── Filtreler ────────────────────────────────────────────
        _section("SETTINGS_FILTERS", "🎛")

        filters = self._cfg.get("filters", {})

        ctk.CTkLabel(f, text=t("SETTINGS_ART")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._art_var = ctk.StringVar(value=filters.get("ausbildungsart", ""))
        ctk.CTkOptionMenu(f, values=AUSBILDUNGSART_OPTIONS, variable=self._art_var, width=260).grid(
            row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        ctk.CTkLabel(f, text=t("SETTINGS_ABSCHLUSS")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._abschluss_var = ctk.StringVar(value=filters.get("abschluss", ""))
        ctk.CTkOptionMenu(f, values=ABSCHLUSS_OPTIONS, variable=self._abschluss_var, width=260).grid(
            row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        ctk.CTkLabel(f, text=t("SETTINGS_BRANCHE")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._branche_var = ctk.StringVar(value=filters.get("branche", ""))
        ctk.CTkOptionMenu(f, values=BRANCHE_OPTIONS, variable=self._branche_var, width=300).grid(
            row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        self._skip_pdf_var = ctk.BooleanVar(value=self._cfg.get("skip_pdf_anschreiben", False))
        ctk.CTkCheckBox(f, text=t("SETTINGS_SKIP_PDF"), variable=self._skip_pdf_var).grid(
            row=row, column=0, columnspan=2, padx=20, pady=(6, 2), sticky="w"); row += 1

        # ── Kişisel bilgiler ──────────────────────────────────────
        _section("SETTINGS_PERSONAL", "👤")

        user_info = self._cfg.get("user_info", {})

        def _info_row(key_label: str, info_key: str, placeholder: str = ""):
            nonlocal row
            ctk.CTkLabel(f, text=t(key_label)).grid(row=row, column=0, padx=20, pady=5, sticky="e")
            var = ctk.StringVar(value=user_info.get(info_key, ""))
            ctk.CTkEntry(f, textvariable=var, width=300, placeholder_text=placeholder).grid(
                row=row, column=1, padx=(0, 20), pady=5, sticky="w")
            row += 1
            return var

        self._v_vorname  = _info_row("SETTINGS_VORNAME",  "vorname",  "Caner")
        self._v_nachname = _info_row("SETTINGS_NACHNAME", "nachname", "Mustermann")
        self._v_strasse  = _info_row("SETTINGS_STRASSE",  "strasse",  "Musterstraße 1")
        self._v_plz      = _info_row("SETTINGS_PLZ",      "plz",      "69115")
        self._v_pstadt   = _info_row("SETTINGS_STADT",    "pstadt",   "Heidelberg")

        # ── SMTP ─────────────────────────────────────────────────
        _section("SETTINGS_SMTP", "📧")

        smtp = self._cfg.get("smtp", {})

        ctk.CTkLabel(f, text=t("SETTINGS_SMTP_HOST")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._smtp_host_var = ctk.StringVar(value=smtp.get("host", ""))
        ctk.CTkEntry(f, textvariable=self._smtp_host_var, width=280, placeholder_text="smtp.gmail.com").grid(
            row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        ctk.CTkLabel(f, text=t("SETTINGS_SMTP_PORT")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._smtp_port_var = ctk.StringVar(value=str(smtp.get("port", 587)))
        ctk.CTkEntry(f, textvariable=self._smtp_port_var, width=100).grid(
            row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        ctk.CTkLabel(f, text=t("SETTINGS_SMTP_EMAIL")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._smtp_email_var = ctk.StringVar(value=smtp.get("email", ""))
        ctk.CTkEntry(f, textvariable=self._smtp_email_var, width=280).grid(
            row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        ctk.CTkLabel(f, text=t("SETTINGS_SMTP_PASS")).grid(row=row, column=0, padx=20, pady=6, sticky="e")
        self._smtp_pass_var = ctk.StringVar(value=smtp.get("password", ""))
        self._smtp_pass_entry = ctk.CTkEntry(f, textvariable=self._smtp_pass_var, width=280, show="*")
        self._smtp_pass_entry.grid(row=row, column=1, padx=(0, 20), pady=6, sticky="w"); row += 1

        ctk.CTkCheckBox(f, text=t("SETTINGS_SMTP_SHOW"), command=self._toggle_smtp_pass).grid(
            row=row, column=1, padx=(0, 20), pady=(0, 4), sticky="w"); row += 1

        self._smtp_tls_var = ctk.BooleanVar(value=smtp.get("use_tls", True))
        ctk.CTkCheckBox(f, text=t("SETTINGS_SMTP_TLS"), variable=self._smtp_tls_var).grid(
            row=row, column=0, columnspan=2, padx=20, pady=4, sticky="w"); row += 1

        smtp_btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        smtp_btn_frame.grid(row=row, column=0, columnspan=2, padx=20, pady=(6, 2), sticky="w"); row += 1
        ctk.CTkButton(smtp_btn_frame, text=t("SETTINGS_SMTP_TEST"), width=180, command=self._test_smtp).pack(side="left", padx=(0, 12))
        self._smtp_status = ctk.CTkLabel(smtp_btn_frame, text="", text_color="gray")
        self._smtp_status.pack(side="left")

        # ── Tarayıcı ─────────────────────────────────────────────
        _section("SETTINGS_BROWSER", "🌐")

        self._headless_var = ctk.BooleanVar(value=self._cfg.get("headless", False))
        ctk.CTkCheckBox(f, text=t("SETTINGS_HEADLESS"), variable=self._headless_var).grid(
            row=row, column=0, columnspan=2, padx=20, pady=6, sticky="w"); row += 1

        # ── Kaydet ───────────────────────────────────────────────
        sep_bottom = ctk.CTkFrame(f, height=1, fg_color=("gray75", "gray35"))
        sep_bottom.grid(row=row, column=0, columnspan=2, padx=16, pady=(12, 0), sticky="ew"); row += 1

        save_row = ctk.CTkFrame(f, fg_color="transparent")
        save_row.grid(row=row, column=0, columnspan=2, padx=16, pady=(10, 24), sticky="w"); row += 1

        ctk.CTkButton(
            save_row, text=t("SETTINGS_SAVE"),
            width=200, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1f6aa5", hover_color="#144d7a",
            command=self._save,
        ).pack(side="left", padx=(0, 16))

        self._status = ctk.CTkLabel(save_row, text="", text_color="#2ecc71", font=ctk.CTkFont(size=12))
        self._status.pack(side="left")

    # ── Helpers ────────────────────────────────────────────────────

    def _toggle_key(self):
        self._api_key_entry.configure(show="" if self._api_key_entry.cget("show") == "*" else "*")

    def _toggle_smtp_pass(self):
        self._smtp_pass_entry.configure(show="" if self._smtp_pass_entry.cget("show") == "*" else "*")

    def _change_lang(self, lang: str):
        from utils.i18n import set_lang
        cfg = load_config()
        cfg["lang"] = lang
        save_config(cfg)
        set_lang(lang)
        # Uygulamayı yeniden başlat
        import sys, os, subprocess, threading
        def _restart():
            import time; time.sleep(0.2)
            if getattr(sys, "frozen", False):
                subprocess.Popen([sys.executable])
            else:
                subprocess.Popen([sys.executable] + sys.argv)
            time.sleep(0.4)
            os._exit(0)
        threading.Thread(target=_restart, daemon=True).start()

    def _test_smtp(self):
        self._smtp_status.configure(text=t("SETTINGS_SMTP_TESTING"), text_color="gray")

        def _do():
            try:
                from services.smtp_service import test_connection
                ok, err = test_connection(
                    host=self._smtp_host_var.get().strip(),
                    port=int(self._smtp_port_var.get().strip() or "587"),
                    login=self._smtp_email_var.get().strip(),
                    password=self._smtp_pass_var.get(),
                    use_tls=self._smtp_tls_var.get(),
                )
                if ok:
                    self._smtp_status.configure(text=t("SETTINGS_SMTP_OK"), text_color="green")
                else:
                    self._smtp_status.configure(text=f"{t('SETTINGS_SMTP_ERR')} {err[:80]}", text_color="#e05555")
            except Exception as e:
                self._smtp_status.configure(text=f"{t('SETTINGS_SMTP_ERR')} {e}", text_color="#e05555")

        threading.Thread(target=_do, daemon=True).start()

    def _get_user_info(self) -> dict:
        return {
            "vorname":  self._v_vorname.get().strip(),
            "nachname": self._v_nachname.get().strip(),
            "strasse":  self._v_strasse.get().strip(),
            "plz":      self._v_plz.get().strip(),
            "stadt":    self._v_pstadt.get().strip(),
            "email":    self._cfg.get("email", ""),
        }

    def _get_smtp_cfg(self) -> dict:
        try:
            port = int(self._smtp_port_var.get().strip() or "587")
        except ValueError:
            port = 587
        return {
            "host":     self._smtp_host_var.get().strip(),
            "port":     port,
            "email":    self._smtp_email_var.get().strip(),
            "password": self._smtp_pass_var.get(),
            "use_tls":  self._smtp_tls_var.get(),
        }

    def _save(self):
        cfg = load_config()
        cfg["openai_key"]           = self._api_key_var.get().strip()
        cfg["user_background"]      = self._bg_text.get("1.0", "end").strip()
        cfg["city"]                 = self._city_var.get().strip()
        cfg["radius"]               = self._radius_var.get()
        cfg["headless"]             = self._headless_var.get()
        cfg["skip_pdf_anschreiben"] = self._skip_pdf_var.get()
        cfg["filters"] = {
            "ausbildungsart": self._art_var.get(),
            "abschluss":      self._abschluss_var.get(),
            "branche":        self._branche_var.get(),
        }
        cfg["user_info"] = self._get_user_info()
        cfg["smtp"]      = self._get_smtp_cfg()
        save_config(cfg)
        self._status.configure(text=t("SETTINGS_SAVED"), text_color="#2ecc71")
        self.after(2500, lambda: self._status.configure(text=""))

    def get_current_config(self) -> dict:
        return {
            "openai_key":           self._api_key_var.get().strip(),
            "user_background":      self._bg_text.get("1.0", "end").strip(),
            "city":                 self._city_var.get().strip(),
            "radius":               self._radius_var.get(),
            "headless":             self._headless_var.get(),
            "skip_pdf_anschreiben": self._skip_pdf_var.get(),
            "filters": {
                "ausbildungsart": self._art_var.get(),
                "abschluss":      self._abschluss_var.get(),
                "branche":        self._branche_var.get(),
            },
            "user_info": self._get_user_info(),
            "smtp":      self._get_smtp_cfg(),
        }
