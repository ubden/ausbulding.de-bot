import json
import os
import sys


def _base_dir() -> str:
    """exe ile çalışırken exe'nin yanı, dev'de proje kökü."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


CONFIG_PATH = os.path.join(_base_dir(), "config.json")

DEFAULTS = {
    "lang": "tr",
    "email": "",
    "password": "",
    "openai_key": "",
    "city": "Heidelberg",
    "radius": "25",
    "user_background": "",
    "headless": False,
    "skip_pdf_anschreiben": False,
    "filters": {
        "ausbildungsart": "",
        "abschluss": "",
        "branche": "",
    },
    "smtp": {
        "host": "",
        "port": 587,
        "email": "",
        "password": "",
        "use_tls": True,
    },
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return dict(DEFAULTS)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULTS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULTS)


def save_config(data: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
