import os
import sys
import subprocess
import webbrowser
import customtkinter as ctk
from utils.config import load_config, save_config
from utils.i18n import t, get_lang, set_lang
from gui.login_tab import LoginTab
from gui.settings_tab import SettingsTab
from gui.bot_tab import BotTab
from gui.applications_tab import ApplicationsTab
from gui.contacts_tab import ContactsTab
from bot.runner import BotRunner

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

LANG_DISPLAY = {"tr": "🇹🇷 TR", "de": "🇩🇪 DE", "en": "🇬🇧 EN"}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(t("APP_TITLE"))
        self.geometry("1160x820")
        self.minsize(960, 650)

        self._runner: BotRunner | None = None
        self._applied_count = 0
        self._scanned_count = 0

        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # ── Başlık çubuğu ─────────────────────────────────────────
        header = ctk.CTkFrame(self, height=58, corner_radius=0, fg_color=("#4a2070", "#2e1248"))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        # Sol: ikon + isim
        left_hdr = ctk.CTkFrame(header, fg_color="transparent")
        left_hdr.grid(row=0, column=0, padx=18, pady=0, sticky="w")
        ctk.CTkLabel(left_hdr, text="🎓", font=ctk.CTkFont(size=26)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            left_hdr, text="AusbildungBot",
            font=ctk.CTkFont(size=21, weight="bold"), text_color="white",
        ).pack(side="left")

        # Orta: slogan
        ctk.CTkLabel(
            header, text=t("APP_SUBTITLE"),
            font=ctk.CTkFont(size=12), text_color="#caa8f0",
        ).grid(row=0, column=1, padx=8, pady=0, sticky="w")

        # Sağ: dil seçici + versiyon
        right_hdr = ctk.CTkFrame(header, fg_color="transparent")
        right_hdr.grid(row=0, column=2, padx=16, pady=0, sticky="e")

        ctk.CTkLabel(
            right_hdr, text=t("LANG_LABEL"),
            font=ctk.CTkFont(size=11), text_color="#9060c0",
        ).pack(side="left", padx=(0, 6))

        cfg_lang = get_lang()
        lang_seg = ctk.CTkSegmentedButton(
            right_hdr,
            values=list(LANG_DISPLAY.values()),
            command=self._on_lang_change,
            width=168, height=30,
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        lang_seg.set(LANG_DISPLAY.get(cfg_lang, "🇹🇷 TR"))
        lang_seg.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(
            right_hdr, text="v2.0",
            font=ctk.CTkFont(size=11), text_color="#6040a0",
        ).pack(side="left")

        # ── Sekmeler ──────────────────────────────────────────────
        self._tabs = ctk.CTkTabview(self, anchor="nw")
        self._tabs.grid(row=1, column=0, padx=10, pady=(8, 0), sticky="nsew")

        for key in ("TAB_LOGIN", "TAB_SETTINGS", "TAB_BOT", "TAB_APPLICATIONS", "TAB_CONTACTS"):
            self._tabs.add(t(key))

        def _tab(key):
            tab = self._tabs.tab(t(key))
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            return tab

        self._login_tab = LoginTab(_tab("TAB_LOGIN"))
        self._login_tab.grid(row=0, column=0, sticky="nsew")

        self._settings_tab = SettingsTab(_tab("TAB_SETTINGS"))
        self._settings_tab.grid(row=0, column=0, sticky="nsew")

        self._bot_tab = BotTab(
            _tab("TAB_BOT"),
            on_start=self._start_bot,
            on_stop=self._stop_bot,
        )
        self._bot_tab.grid(row=0, column=0, sticky="nsew")

        self._apps_tab = ApplicationsTab(_tab("TAB_APPLICATIONS"))
        self._apps_tab.grid(row=0, column=0, sticky="nsew")

        self._contacts_tab = ContactsTab(_tab("TAB_CONTACTS"))
        self._contacts_tab.grid(row=0, column=0, sticky="nsew")

        # ── Footer ────────────────────────────────────────────────
        footer = ctk.CTkFrame(self, height=28, corner_radius=0, fg_color=("#1e0a38", "#110620"))
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(1, weight=1)

        pw_frame = ctk.CTkFrame(footer, fg_color="transparent")
        pw_frame.grid(row=0, column=0, padx=14, pady=4, sticky="w")
        ctk.CTkLabel(
            pw_frame, text=t("FOOTER_POWERED_BY"),
            font=ctk.CTkFont(size=10), text_color="#6a4090",
        ).pack(side="left", padx=(0, 4))
        ub_lbl = ctk.CTkLabel(
            pw_frame, text=t("FOOTER_COMMUNITY"),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#9060c0", cursor="hand2",
        )
        ub_lbl.pack(side="left")
        ub_lbl.bind("<Button-1>", lambda _e: webbrowser.open("https://github.com/ubden"))

        ctk.CTkLabel(
            footer, text=t("FOOTER_VERSION"),
            font=ctk.CTkFont(size=10), text_color="#4a2870",
        ).grid(row=0, column=1, pady=4)

        right_frame = ctk.CTkFrame(footer, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=14, pady=4, sticky="e")
        gh_lbl = ctk.CTkLabel(
            right_frame, text="github.com/ck-cankurt",
            font=ctk.CTkFont(size=10), text_color="#6a4090", cursor="hand2",
        )
        gh_lbl.pack(side="left", padx=(0, 12))
        gh_lbl.bind("<Button-1>", lambda _e: webbrowser.open("https://github.com/ck-cankurt"))
        donate_lbl = ctk.CTkLabel(
            right_frame, text=t("FOOTER_DONATE"),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#b060b0", cursor="hand2",
        )
        donate_lbl.pack(side="left")
        donate_lbl.bind("<Button-1>", lambda _e: webbrowser.open("https://ubd.one/donate"))

    # ── Dil değiştirme ─────────────────────────────────────────────

    def _on_lang_change(self, display_val: str):
        # Görüntü değerinden lang kodunu bul
        rev = {v: k for k, v in LANG_DISPLAY.items()}
        lang = rev.get(display_val)
        if not lang or lang == get_lang():
            return
        cfg = load_config()
        cfg["lang"] = lang
        save_config(cfg)
        # Süreci yeniden başlat
        self.after(200, self._restart)

    @staticmethod
    def _restart():
        if getattr(sys, "frozen", False):
            subprocess.Popen([sys.executable])
        else:
            subprocess.Popen([sys.executable] + sys.argv)
        # Kısa gecikme sonra pencereyi kapat
        import threading
        def _quit():
            import time; time.sleep(0.4)
            os._exit(0)
        threading.Thread(target=_quit, daemon=True).start()

    # ── Bot başlatma / durdurma ────────────────────────────────────

    def _start_bot(self):
        if self._runner and self._runner.is_running():
            return

        email, password = self._login_tab.get_credentials()
        if not email or not password:
            self._bot_tab.push_log(t("RUNNER_NO_CREDS"))
            self._bot_tab.push_stopped()
            return

        cfg = load_config()
        cfg.update(self._settings_tab.get_current_config())
        cfg["email"]    = email
        cfg["password"] = password
        cfg["keyword"]  = self._bot_tab.get_keyword()
        cfg["lang"]     = get_lang()
        save_config(cfg)

        self._applied_count = 0
        self._scanned_count = 0

        self._runner = BotRunner(
            config=cfg,
            log_callback=self._on_log,
            status_callback=self._on_status,
            job_callback=self._on_job_done,
        )

        import threading
        def _watch():
            self._runner._thread.join()
            self._bot_tab.push_stopped()
        threading.Thread(target=_watch, daemon=True).start()

        self._runner.start()

    def _stop_bot(self):
        if self._runner:
            self._runner.stop()

    def _on_log(self, text: str):
        self._bot_tab.push_log(text)

    def _on_status(self, text: str):
        self._bot_tab.push_status(text)

    def _on_job_done(self, job: dict):
        self._scanned_count += 1
        if job.get("status") == "applied":
            self._applied_count += 1
        self._bot_tab.push_counter(
            f"{t('RUNNER_APPLIED')} {self._applied_count}  |  "
            f"{t('RUNNER_SKIPPED')} {self._scanned_count}"
        )
        self._apps_tab.add_job(job)
        try:
            self._contacts_tab.after(0, self._contacts_tab._load)
        except Exception:
            pass
