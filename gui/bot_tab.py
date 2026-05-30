import queue
import customtkinter as ctk
from datetime import datetime
from utils.i18n import t

_MAX_QUEUE_ITEMS = 25
_MAX_LOG_LINES = 1200

_LOG_TAG_COLORS = {
    "log_time":     "#7f8c8d",
    "log_default":  "#d9d9e3",
    "log_progress": "#64b5f6",
    "log_success":  "#2ecc71",
    "log_warning":  "#f5b041",
    "log_error":    "#ff6b6b",
    "log_telegram": "#4dd0e1",
}


class BotTab(ctk.CTkFrame):
    def __init__(self, master, on_start, on_stop, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_start  = on_start
        self._on_stop   = on_stop
        self._log_queue: queue.Queue = queue.Queue()
        self._running   = False
        self._build()
        self._poll_queue()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ── Kontrol kartı ────────────────────────────────────────
        ctrl_card = ctk.CTkFrame(self, corner_radius=12, border_width=1, border_color=("gray78", "gray30"))
        ctrl_card.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")
        ctrl_card.grid_columnconfigure(0, weight=1)

        ctrl_hdr = ctk.CTkFrame(ctrl_card, fg_color=("#5b2d8e", "#3d1f63"), corner_radius=10)
        ctrl_hdr.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        ctk.CTkLabel(
            ctrl_hdr, text=t("BOT_HEADER"),
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white",
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        btn_row = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        btn_row.grid(row=1, column=0, padx=16, pady=(14, 6), sticky="ew")
        btn_row.grid_columnconfigure(3, weight=1)

        self._start_btn = ctk.CTkButton(
            btn_row, text=t("BOT_START"), width=160, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1a9b4f", hover_color="#147a3e",
            command=self._start,
        )
        self._start_btn.grid(row=0, column=0, padx=(0, 10))

        self._stop_btn = ctk.CTkButton(
            btn_row, text=t("BOT_STOP"), width=130, height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#c0392b", hover_color="#922b21",
            command=self._stop, state="disabled",
        )
        self._stop_btn.grid(row=0, column=1, padx=(0, 10))

        ctk.CTkButton(
            btn_row, text=t("BOT_CLEAR_LOG"), width=140, height=40,
            font=ctk.CTkFont(size=12),
            fg_color=("gray60", "gray35"), hover_color=("gray45", "gray25"),
            command=self._clear_log,
        ).grid(row=0, column=2)

        # ── Kelime filtresi ──────────────────────────────────────
        sep = ctk.CTkFrame(ctrl_card, height=1, fg_color=("gray78", "gray32"))
        sep.grid(row=2, column=0, padx=16, pady=(10, 0), sticky="ew")

        kw_frame = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        kw_frame.grid(row=3, column=0, padx=16, pady=(10, 16), sticky="ew")
        kw_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            kw_frame, text=t("BOT_KEYWORD_LABEL"),
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        self._keyword_var = ctk.StringVar()
        ctk.CTkEntry(
            kw_frame, textvariable=self._keyword_var,
            width=300, height=36,
            placeholder_text=t("BOT_KEYWORD_PH"),
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=1, padx=(0, 16), sticky="w")

        ctk.CTkLabel(
            kw_frame, text=t("BOT_KEYWORD_HINT"),
            font=ctk.CTkFont(size=10), text_color="gray", justify="left",
        ).grid(row=0, column=2, sticky="w")

        # ── Durum çubuğu ─────────────────────────────────────────
        status_card = ctk.CTkFrame(
            self, corner_radius=10,
            fg_color=("gray90", "gray20"),
            border_width=1, border_color=("gray78", "gray32"),
        )
        status_card.grid(row=1, column=0, padx=16, pady=(0, 6), sticky="ew")
        status_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            status_card, text=t("BOT_STATUS_LABEL"),
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, padx=(14, 6), pady=10)

        self._status_label = ctk.CTkLabel(
            status_card, text=t("BOT_STATUS_WAITING"),
            font=ctk.CTkFont(size=12), anchor="w",
        )
        self._status_label.grid(row=0, column=1, padx=4, pady=10, sticky="w")

        self._counter_label = ctk.CTkLabel(
            status_card, text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1a9b4f", "#2ecc71"),
        )
        self._counter_label.grid(row=0, column=2, padx=(8, 16), pady=10)

        # ── Log başlığı + kutusu ─────────────────────────────────
        ctk.CTkLabel(
            self, text=t("BOT_LOG_HEADER"),
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=2, column=0, padx=16, pady=(2, 2), sticky="w")

        self._log_box = ctk.CTkTextbox(
            self, state="disabled",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=10, border_width=1, border_color=("gray78", "gray32"),
        )
        self._log_box.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="nsew")
        self._configure_log_tags()

    # ── Eylemler ──────────────────────────────────────────────────

    def _start(self):
        self._running = True
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._set_status(t("BOT_STARTING"))
        self._on_start()

    def _stop(self):
        self._stop_btn.configure(state="disabled")
        self._set_status(t("BOT_STOPPING"))
        self._on_stop()

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    def _set_status(self, text: str):
        self._status_label.configure(text=text)

    # ── Kuyruk ────────────────────────────────────────────────────

    def _poll_queue(self):
        logs = []
        status_text = None
        counter_text = None
        stopped = False

        for _ in range(_MAX_QUEUE_ITEMS):
            try:
                item = self._log_queue.get_nowait()
            except queue.Empty:
                break

            tp = item["type"]
            if tp == "log":
                logs.append(item["text"])
            elif tp == "status":
                status_text = item["text"]
            elif tp == "stopped":
                stopped = True
            elif tp == "counter":
                counter_text = item["text"]

        if logs:
            self._append_logs(logs)
        if status_text is not None:
            self._set_status(status_text)
        if counter_text is not None:
            self._counter_label.configure(text=counter_text)
        if stopped:
            self._on_bot_stopped()

        self.after(50 if not self._log_queue.empty() else 150, self._poll_queue)

    def _text_widget(self):
        return getattr(self._log_box, "_textbox", self._log_box)

    def _configure_log_tags(self):
        widget = self._text_widget()
        for tag, color in _LOG_TAG_COLORS.items():
            try:
                widget.tag_configure(tag, foreground=color)
            except Exception:
                pass

    def _classify_log(self, text: str) -> str:
        s = text.lower()
        if "telegram" in s:
            return "log_telegram"
        if any(x in s for x in ("hata", "error", "fehler", "başarısız", "failed", "exception")):
            return "log_error"
        if any(x in s for x in ("atlandı", "zaten", "bulunamadı", "uyarı", "gerekli", "skipped", "warning")):
            return "log_warning"
        if any(x in s for x in ("✓", "✅", "başvuru gönderildi", "onaylandı", "tamamlandı", "başarılı", "kaydedildi", "done")):
            return "log_success"
        if any(x in s for x in ("başvuruluyor", "aranıyor", "yükleniyor", "taranıyor", "adım", "tıklandı", "scanning", "applying")):
            return "log_progress"
        return "log_default"

    def _append_logs(self, texts: list[str]):
        widget = self._text_widget()
        self._log_box.configure(state="normal")
        for text in texts:
            ts = datetime.now().strftime("%H:%M:%S")
            tag = self._classify_log(text)
            try:
                widget.insert("end", f"[{ts}] ", ("log_time",))
                widget.insert("end", f"{text}\n", (tag,))
            except Exception:
                self._log_box.insert("end", f"[{ts}] {text}\n")
        self._trim_log(widget)
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _trim_log(self, widget):
        try:
            line_count = int(widget.index("end-1c").split(".")[0])
            if line_count > _MAX_LOG_LINES:
                delete_to = line_count - _MAX_LOG_LINES + 1
                widget.delete("1.0", f"{delete_to}.0")
        except Exception:
            pass

    def _append_log(self, text: str):
        self._append_logs([text])

    def _on_bot_stopped(self):
        self._running = False
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")

    # ── Public API ────────────────────────────────────────────────

    def get_keyword(self) -> str:
        return self._keyword_var.get().strip()

    def push_log(self, text: str):
        self._log_queue.put({"type": "log", "text": text})

    def push_status(self, text: str):
        self._log_queue.put({"type": "status", "text": text})

    def push_stopped(self):
        self._log_queue.put({"type": "stopped"})

    def push_counter(self, text: str):
        self._log_queue.put({"type": "counter", "text": text})
