import threading
import os
from bot.browser import BrowserManager
from bot.login import login
from bot.scraper import scrape_jobs
from bot.applicator import apply_to_job
from services.database import upsert_application, job_exists
from services.telegram_service import build_application_message, send_document, send_message
from utils.i18n import t


class BotRunner:
    def __init__(self, config: dict, log_callback, status_callback, job_callback):
        self.config = config
        self.log = log_callback
        self.set_status = status_callback
        self.on_job_done = job_callback
        self._stop_event = threading.Event()
        self._thread: threading.Thread = None
        self._browser = BrowserManager()
        self._telegram_warning_logged = False

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self.log(t("RUNNER_STOPPING"))
        # Close browser to interrupt blocking Playwright operations
        try:
            self._browser.stop()
        except Exception:
            pass

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        cfg = self.config
        self.set_status(t("RUNNER_BROWSER_START"))

        try:
            page = self._browser.start(headless=cfg.get("headless", False))
        except Exception as e:
            self.log(f"{t('RUNNER_BROWSER_ERR')} {e}")
            self.set_status(t("RUNNER_ERROR_STATUS"))
            return

        applied = 0
        skipped = 0
        errors  = 0

        try:
            # Login
            self.set_status(t("RUNNER_LOGGING_IN"))
            ok = login(page, cfg["email"], cfg["password"], log=self.log)
            if not ok:
                self.set_status(t("RUNNER_LOGIN_FAIL"))
                return

            if self._stop_event.is_set():
                self.set_status(t("RUNNER_STOPPED"))
                return

            # Scan listings
            self.set_status(t("RUNNER_SCANNING"))
            jobs = scrape_jobs(
                page,
                city=cfg.get("city", ""),
                radius=cfg.get("radius", "25"),
                filters=cfg.get("filters", {}),
                keyword=cfg.get("keyword", ""),
                log=self.log,
                stop_event=self._stop_event,
            )

            if not jobs:
                self.log(t("RUNNER_NO_JOBS"))
                self.set_status(t("RUNNER_NO_JOBS_STATUS"))
                return

            for i, job in enumerate(jobs, 1):
                if self._stop_event.is_set():
                    break

                self.set_status(f"{i}/{len(jobs)} — {job['title'][:40]}")

                if job_exists(job["job_id"]):
                    self.log(f"[{i}/{len(jobs)}] {t('RUNNER_SKIPPED_DB')} {job['title'][:60]}")
                    skipped += 1
                    continue

                self.log(f"[{i}/{len(jobs)}] {t('RUNNER_APPLYING')} {job['title'][:60]}")
                status, error_msg, pdf_path = apply_to_job(
                    page,
                    job,
                    openai_key=cfg.get("openai_key", ""),
                    user_background=cfg.get("user_background", ""),
                    user_info=cfg.get("user_info", {}),
                    log=self.log,
                    stop_event=self._stop_event,
                    skip_pdf_anschreiben=cfg.get("skip_pdf_anschreiben", False),
                )

                upsert_application(
                    job_id=job["job_id"],
                    title=job["title"],
                    company=job["company"],
                    location=job["location"],
                    url=job["url"],
                    status=status,
                    error=error_msg or None,
                    pdf_path=pdf_path or None,
                )
                job_result = {**job, "status": status, "pdf_path": pdf_path or None}
                self.on_job_done(job_result)

                if status == "applied":
                    applied += 1
                    self._send_telegram_notification(job_result)
                elif status in ("skipped", "already_applied"):
                    skipped += 1
                else:
                    errors += 1

        except Exception as e:
            if not self._stop_event.is_set():
                self.log(f"{t('RUNNER_BOT_ERR')} {e}")
                self.set_status(t("RUNNER_ERROR_STATUS"))
            else:
                self.set_status(t("RUNNER_STOPPED"))
        finally:
            try:
                self._browser.stop()
            except Exception:
                pass

            a_lbl = t("RUNNER_APPLIED")
            s_lbl = t("RUNNER_SKIPPED")
            e_lbl = t("RUNNER_ERRORS")
            summary_detail = f"{a_lbl} {applied}  |  {s_lbl} {skipped}  |  {e_lbl} {errors}"

            if self._stop_event.is_set():
                self.log(f"{t('RUNNER_STOPPED')} — {summary_detail}")
                self.set_status(f"{t('RUNNER_STOPPED')} — {a_lbl} {applied}")
            else:
                full = f"{t('RUNNER_DONE')} — {summary_detail}"
                self.log(full)
                self.set_status(full)

    def _send_telegram_notification(self, job: dict) -> None:
        tg_cfg = self.config.get("telegram") or {}
        if not tg_cfg.get("enabled"):
            return

        token = (tg_cfg.get("token") or "").strip()
        chat_id = (tg_cfg.get("chat_id") or "").strip()
        if not token or not chat_id:
            if not self._telegram_warning_logged:
                self.log("Telegram: token veya Chat ID eksik, bildirim atlandı.")
                self._telegram_warning_logged = True
            return

        msg = build_application_message(
            title=job.get("title", ""),
            company=job.get("company", ""),
            location=job.get("location", ""),
            url=job.get("url", ""),
            lang=self.config.get("lang", "tr"),
            cover_letter=job.get("anschreiben_text", ""),
        )

        def _send():
            ok, err = send_message(token, chat_id, msg)
            title = (job.get("title") or "")[:60]
            if ok:
                self.log(f"Telegram: bildirim gönderildi — {title}")
            else:
                self.log(f"Telegram: bildirim gönderilemedi — {err[:100]}")
                return

            pdf_path = job.get("pdf_path") or ""
            if not pdf_path or not os.path.isfile(pdf_path):
                return

            caption = "📄 <b>Anschreiben PDF</b>"
            doc_ok, doc_err = send_document(token, chat_id, pdf_path, caption=caption)
            if doc_ok:
                self.log(f"Telegram: Anschreiben PDF gönderildi — {title}")
            else:
                self.log(f"Telegram: PDF gönderilemedi — {doc_err[:100]}")

        threading.Thread(target=_send, daemon=True).start()
