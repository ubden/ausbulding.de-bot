import sys
import os

# ── Frozen (exe) ortamında Playwright tarayıcı yolunu exe yanına yönlendir ──
if getattr(sys, "frozen", False):
    _exe_dir = os.path.dirname(sys.executable)
    # Tarayıcıları exe'nin yanındaki "playwright_browsers" klasöründe tut
    os.environ.setdefault(
        "PLAYWRIGHT_BROWSERS_PATH",
        os.path.join(_exe_dir, "playwright_browsers"),
    )
    # Playwright node driver'ının sys._MEIPASS içindeki konumunu göster
    _driver_dir = os.path.join(sys._MEIPASS, "playwright", "_impl", "_driver")
    if os.path.isdir(_driver_dir):
        os.environ.setdefault("PLAYWRIGHT_DRIVER_PATH", _driver_dir)
else:
    # Geliştirme ortamı — proje kökünü path'e ekle
    sys.path.insert(0, os.path.dirname(__file__))

from utils.i18n import init_from_config
from services.database import init_db
from gui.app import App


def main():
    init_from_config()   # i18n dilini config'den yükle
    init_db()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
