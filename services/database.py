import sqlite3
import os
import sys
from datetime import datetime


def _base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DB_PATH = os.path.join(_base_dir(), "applications.db")
APPLICATION_KEYS = [
    "job_id", "title", "company", "location", "url", "status",
    "error_message", "applied_at", "created_at", "pdf_path",
]
APPLICATION_SELECT = (
    "SELECT job_id, title, company, location, url, status, "
    "error_message, applied_at, created_at, pdf_path FROM applications"
)


def _connect():
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                title TEXT,
                company TEXT,
                location TEXT,
                url TEXT,
                status TEXT,
                error_message TEXT,
                applied_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                pdf_path TEXT
            )
        """)
        # Sütun zaten varsa ALTER TABLE sessizce başarısız olur — güvenli migration
        try:
            conn.execute("ALTER TABLE applications ADD COLUMN pdf_path TEXT")
        except Exception:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                company TEXT,
                job_title TEXT,
                contact_name TEXT,
                contact_position TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                job_url TEXT,
                mail_sent INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def upsert_application(
    job_id: str,
    title: str,
    company: str,
    location: str,
    url: str,
    status: str,
    error: str = None,
    pdf_path: str = None,
) -> None:
    applied_at = datetime.now().isoformat() if status == "applied" else None
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO applications
                (job_id, title, company, location, url, status, error_message, applied_at, pdf_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                status        = excluded.status,
                error_message = excluded.error_message,
                applied_at    = COALESCE(excluded.applied_at, applied_at),
                pdf_path      = COALESCE(excluded.pdf_path, pdf_path)
            """,
            (job_id, title, company, location, url, status, error, applied_at, pdf_path),
        )
        conn.commit()


def job_exists(job_id: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT status FROM applications WHERE job_id = ?", (job_id,)
        ).fetchone()
    if row is None:
        return False
    return row[0] in ("applied", "already_applied")


def get_all_applications() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            f"{APPLICATION_SELECT} ORDER BY created_at DESC"
        ).fetchall()
    return [dict(zip(APPLICATION_KEYS, row)) for row in rows]


def get_applications_page(limit: int = 50, offset: int = 0) -> list[dict]:
    limit = max(1, int(limit or 50))
    offset = max(0, int(offset or 0))
    with _connect() as conn:
        rows = conn.execute(
            f"{APPLICATION_SELECT} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    return [dict(zip(APPLICATION_KEYS, row)) for row in rows]


def get_applications_count() -> int:
    with _connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]


def get_stats() -> dict:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) FROM applications GROUP BY status"
        ).fetchall()
    stats = {"applied": 0, "already_applied": 0, "skipped": 0, "error": 0}
    for status, count in rows:
        stats[status] = count
    return stats


def clear_all() -> int:
    """Tüm kayıtları sil. Silinen satır sayısını döndür."""
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        conn.execute("DELETE FROM applications")
        conn.commit()
    return count


# ── Contacts ──────────────────────────────────────────────────────────

def upsert_contact(
    job_id: str,
    company: str,
    job_title: str,
    contact_name: str,
    contact_position: str,
    contact_email: str,
    contact_phone: str,
    job_url: str,
) -> None:
    """Aynı job_id + contact_email kombinasyonu varsa güncelle, yoksa ekle."""
    with _connect() as conn:
        existing = conn.execute(
            "SELECT id FROM contacts WHERE job_id=? AND contact_email=?",
            (job_id, contact_email),
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE contacts SET company=?, job_title=?, contact_name=?,
                   contact_position=?, contact_phone=?, job_url=? WHERE id=?""",
                (company, job_title, contact_name, contact_position,
                 contact_phone, job_url, existing[0]),
            )
        else:
            conn.execute(
                """INSERT INTO contacts
                   (job_id, company, job_title, contact_name, contact_position,
                    contact_email, contact_phone, job_url)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (job_id, company, job_title, contact_name, contact_position,
                 contact_email, contact_phone, job_url),
            )
        conn.commit()


def get_all_contacts() -> list[dict]:
    keys = [
        "id", "job_id", "company", "job_title", "contact_name",
        "contact_position", "contact_email", "contact_phone",
        "job_url", "mail_sent", "created_at",
    ]
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, job_id, company, job_title, contact_name, "
            "contact_position, contact_email, contact_phone, job_url, "
            "mail_sent, created_at FROM contacts ORDER BY created_at DESC"
        ).fetchall()
    return [dict(zip(keys, r)) for r in rows]


def mark_mail_sent(contact_id: int) -> None:
    with _connect() as conn:
        conn.execute("UPDATE contacts SET mail_sent=1 WHERE id=?", (contact_id,))
        conn.commit()
