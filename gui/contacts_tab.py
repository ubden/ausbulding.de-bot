import queue
import threading
import time
import customtkinter as ctk
from services.database import get_all_contacts, mark_mail_sent
from utils.i18n import t

DEFAULT_SUBJECT = "Bewerbung als {pozisyon} – Nachfrage"

DEFAULT_TEMPLATE = """\
Sehr geehrte/r {kontakt_adi},

ich habe mich kürzlich über ausbildung.de als {pozisyon} bei {firma_adi} beworben \
und möchte mein Interesse nochmals bekräftigen.

Ich bin sehr motiviert und würde mich über eine Rückmeldung sehr freuen.

Mit freundlichen Grüßen,
{vorname} {nachname}"""

# (i18n key, width) — headers resolved at runtime
_COL_DEFS = [
    ("CON_COL_COMPANY",  185),
    ("CON_COL_POSITION", 185),
    ("CON_COL_NAME",     130),
    ("CON_COL_ROLE",     130),
    ("CON_COL_EMAIL",    210),
    ("CON_COL_PHONE",    110),
    ("CON_COL_MAIL",      80),
]


def _columns():
    return [(t(key), width) for key, width in _COL_DEFS]


class ContactsTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._contacts: list[dict] = []
        self._build()
        self._load()

    # ── Layout ────────────────────────────────────────────────────────

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ── Üst kart: başlık + butonlar ──────────────────────────────
        top_card = ctk.CTkFrame(self, corner_radius=12, border_width=1, border_color=("gray78", "gray30"))
        top_card.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="ew")
        top_card.grid_columnconfigure(0, weight=1)

        top_hdr = ctk.CTkFrame(top_card, fg_color=("#5b2d8e", "#3d1f63"), corner_radius=10)
        top_hdr.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        top_hdr.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            top_hdr, text=t("CON_HEADER"),
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white",
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self._progress_label = ctk.CTkLabel(
            top_hdr, text="", text_color="#caa8f0", font=ctk.CTkFont(size=11)
        )
        self._progress_label.grid(row=0, column=1, padx=12, pady=10, sticky="e")

        # Buton satırı
        btn_row = ctk.CTkFrame(top_card, fg_color="transparent")
        btn_row.grid(row=1, column=0, padx=14, pady=(10, 14), sticky="ew")

        ctk.CTkButton(
            btn_row, text=t("CON_REFRESH"), width=110, height=34,
            fg_color=("gray60", "gray38"), hover_color=("gray45", "gray26"),
            command=self._load,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text=t("CON_SEND_ALL"), width=185, height=34,
            fg_color="#1f6aa5", hover_color="#144d7a",
            command=self._send_all,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text=t("CON_SEND_UNSENT"), width=230, height=34,
            fg_color="#2d6a2d", hover_color="#1e4d1e",
            command=self._send_unsent,
        ).pack(side="left")

        # ── Şablon editörü ────────────────────────────────────────────
        tmpl_card = ctk.CTkFrame(self, corner_radius=12, border_width=1, border_color=("gray78", "gray30"))
        tmpl_card.grid(row=1, column=0, padx=16, pady=(0, 6), sticky="ew")
        tmpl_card.grid_columnconfigure(1, weight=1)

        tmpl_hdr = ctk.CTkFrame(tmpl_card, fg_color=("gray82", "gray26"), corner_radius=10)
        tmpl_hdr.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="ew")
        ctk.CTkLabel(
            tmpl_hdr, text=t("CON_TMPL_HEADER"),
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=8, sticky="w")
        ctk.CTkLabel(
            tmpl_hdr, text=t("CON_TMPL_VARS"),
            font=ctk.CTkFont(size=10), text_color="gray",
        ).grid(row=0, column=1, padx=(0, 16), pady=8, sticky="e")

        ctk.CTkLabel(tmpl_card, text=t("CON_TMPL_SUBJECT"), font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, padx=(16, 8), pady=(10, 6), sticky="e")
        self._subject_var = ctk.StringVar(value=DEFAULT_SUBJECT)
        ctk.CTkEntry(tmpl_card, textvariable=self._subject_var, height=34,
                     font=ctk.CTkFont(size=12)).grid(
            row=1, column=1, padx=(0, 16), pady=(10, 6), sticky="ew")

        ctk.CTkLabel(tmpl_card, text=t("CON_TMPL_BODY"), font=ctk.CTkFont(size=12), anchor="ne").grid(
            row=2, column=0, padx=(16, 8), pady=(0, 12), sticky="ne")
        self._tmpl_box = ctk.CTkTextbox(tmpl_card, height=110, wrap="word", font=ctk.CTkFont(size=12))
        self._tmpl_box.insert("1.0", DEFAULT_TEMPLATE)
        self._tmpl_box.grid(row=2, column=1, padx=(0, 16), pady=(0, 12), sticky="ew")

        # ── Tablo başlıkları ──────────────────────────────────────────
        hdr_frame = ctk.CTkFrame(self, fg_color=("gray82", "gray26"), corner_radius=8)
        hdr_frame.grid(row=2, column=0, padx=16, pady=(0, 2), sticky="ew")
        for col_i, (label, width) in enumerate(_columns()):
            ctk.CTkLabel(
                hdr_frame, text=label, width=width,
                font=ctk.CTkFont(size=12, weight="bold"), anchor="w",
            ).grid(row=0, column=col_i, padx=(8, 4), pady=7, sticky="w")
        ctk.CTkLabel(
            hdr_frame, text=t("CON_COL_ACTION"), width=90,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=len(_COL_DEFS), padx=(4, 8), pady=7)

        # ── Scroll alanı ─────────────────────────────────────────────
        self._scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray96", "gray14"),
            corner_radius=8,
            border_width=1,
            border_color=("gray78", "gray30"),
        )
        self._scroll.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="nsew")

    def _load(self):
        for child in self._scroll.winfo_children():
            child.destroy()

        self._contacts = get_all_contacts()
        for i, c in enumerate(self._contacts):
            self._add_row(i, c)

        sent = sum(1 for c in self._contacts if c["mail_sent"])
        self._progress_label.configure(
            text=t("CON_PROGRESS", n=len(self._contacts), s=sent)
        )

    def _add_row(self, i: int, c: dict):
        cols = _columns()
        bg = ("gray92", "gray17") if i % 2 == 0 else ("white", "gray21")
        row_frame = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=5)
        row_frame.grid(row=i, column=0, padx=4, pady=1, sticky="ew")
        self._scroll.grid_columnconfigure(0, weight=1)

        sent = bool(c.get("mail_sent"))
        values = [
            c.get("company", ""),
            c.get("job_title", ""),
            c.get("contact_name", ""),
            c.get("contact_position", ""),
            c.get("contact_email", ""),
            c.get("contact_phone", ""),
            t("CON_SENT") if sent else t("CON_NOT_SENT"),
        ]

        for col_i, (val, (_, width)) in enumerate(zip(values, cols)):
            if col_i == 6:
                color = "#2ecc71" if sent else ("gray55", "gray55")
            else:
                color = ("gray10", "gray90")
            ctk.CTkLabel(
                row_frame, text=str(val)[:52], width=width,
                anchor="w", text_color=color,
                font=ctk.CTkFont(size=11),
            ).grid(row=0, column=col_i, padx=(8, 4), pady=5, sticky="w")

        if c.get("contact_email") and not sent:
            ctk.CTkButton(
                row_frame, text=t("CON_SEND_BTN"), width=82, height=28,
                fg_color="#1f6aa5", hover_color="#144d7a",
                font=ctk.CTkFont(size=11),
                command=lambda contact=c: self._send_single(contact),
            ).grid(row=0, column=len(_COL_DEFS), padx=(4, 8), pady=4)
        else:
            ctk.CTkLabel(row_frame, text="", width=82).grid(
                row=0, column=len(_COL_DEFS), padx=(4, 8), pady=4)

    # ── Mail gönderme ────────────────────────────────────────────────

    def _get_smtp_cfg(self) -> dict | None:
        try:
            from utils.config import load_config
            smtp = load_config().get("smtp", {})
            if not smtp.get("host") or not smtp.get("email"):
                return None
            return smtp
        except Exception:
            return None

    def _get_sender_name(self) -> tuple[str, str]:
        try:
            from utils.config import load_config
            ui = load_config().get("user_info", {})
            return ui.get("vorname", ""), ui.get("nachname", "")
        except Exception:
            return "", ""

    def _build_mail(self, contact: dict) -> tuple[str, str]:
        vorname, nachname = self._get_sender_name()
        reps = {
            "{kontakt_adi}": contact.get("contact_name", ""),
            "{firma_adi}":   contact.get("company", ""),
            "{pozisyon}":    contact.get("job_title", ""),
            "{vorname}":     vorname,
            "{nachname}":    nachname,
        }
        subject = self._subject_var.get()
        body    = self._tmpl_box.get("1.0", "end").strip()
        for k, v in reps.items():
            subject = subject.replace(k, v)
            body    = body.replace(k, v)
        return subject, body

    def _no_smtp_warning(self):
        self._set_progress(t("CON_NO_SMTP"), color="#e05555")

    def _send_single(self, contact: dict):
        smtp = self._get_smtp_cfg()
        if not smtp:
            self._no_smtp_warning()
            return
        threading.Thread(target=self._do_send, args=([contact], smtp, False), daemon=True).start()

    def _send_all(self):
        lst = [c for c in self._contacts if c.get("contact_email")]
        if not lst:
            self._set_progress(t("CON_NO_CONTACTS"), color="gray")
            return
        smtp = self._get_smtp_cfg()
        if not smtp:
            self._no_smtp_warning()
            return
        threading.Thread(target=self._do_send, args=(lst, smtp, True), daemon=True).start()

    def _send_unsent(self):
        lst = [c for c in self._contacts if c.get("contact_email") and not c.get("mail_sent")]
        if not lst:
            self._set_progress(t("CON_ALL_SENT"), color="gray")
            return
        smtp = self._get_smtp_cfg()
        if not smtp:
            self._no_smtp_warning()
            return
        threading.Thread(target=self._do_send, args=(lst, smtp, True), daemon=True).start()

    def _do_send(self, contacts: list[dict], smtp: dict, with_delay: bool):
        from services.smtp_service import send_email
        total = len(contacts)

        for idx, contact in enumerate(contacts, 1):
            email_addr = contact.get("contact_email", "")
            if not email_addr:
                continue

            subject, body = self._build_mail(contact)
            self._set_progress(t("CON_SENDING", i=idx, n=total, addr=email_addr[:40]))

            ok, err = send_email(
                host=smtp["host"],
                port=int(smtp.get("port", 587)),
                login=smtp["email"],
                password=smtp["password"],
                to_addr=email_addr,
                subject=subject,
                body=body,
                use_tls=smtp.get("use_tls", True),
            )

            if ok:
                try:
                    mark_mail_sent(contact["id"])
                except Exception:
                    pass
                self._set_progress(
                    t("CON_SENT_OK", i=idx, n=total, addr=email_addr[:40]),
                    color="#2ecc71",
                )
            else:
                self._set_progress(
                    t("CON_ERR", addr=email_addr[:30], err=err[:60]),
                    color="#e05555",
                )

            if with_delay and idx < total:
                for remaining in range(5, 0, -1):
                    self._set_progress(
                        t("CON_WAIT", i=idx, n=total, r=remaining)
                    )
                    time.sleep(1)

        self.after(0, self._load)
        self._set_progress(t("CON_DONE", n=total), color="#2ecc71")

    def _set_progress(self, text: str, color: str = "#caa8f0"):
        self.after(0, lambda: self._progress_label.configure(text=text, text_color=color))
