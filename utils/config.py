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
    "user_info": {
        "vorname": "",
        "nachname": "",
        "strasse": "",
        "plz": "",
        "stadt": "",
        "email": "",
    },
    "smtp": {
        "host": "",
        "port": 587,
        "email": "",
        "password": "",
        "use_tls": True,
    },
    "telegram": {
        "enabled":  False,
        "token":    "",
        "chat_id":  "",
    },
}


def _merge_defaults(defaults: dict, data: dict) -> dict:
    merged = dict(defaults)
    for key, value in (data or {}).items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = _merge_defaults(merged[key], value)
        else:
            merged[key] = value
    return merged


def _normalize_config(cfg: dict) -> dict:
    user_info = cfg.setdefault("user_info", {})
    if not user_info.get("stadt") and user_info.get("pstadt"):
        user_info["stadt"] = user_info.get("pstadt", "")
    user_info.pop("pstadt", None)
    return cfg


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return _normalize_config(_merge_defaults(DEFAULTS, {}))
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _normalize_config(_merge_defaults(DEFAULTS, data))
    except Exception:
        return _normalize_config(_merge_defaults(DEFAULTS, {}))


def save_config(data: dict) -> None:
    data = _normalize_config(_merge_defaults(DEFAULTS, data or {}))
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
