# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — AusbildungBot
  Çıktı: dist/AusbildungBot/AusbildungBot.exe  (onedir modu)
"""

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# ── Veri / binary toplama ──────────────────────────────────────────────────
ctk_datas,     ctk_bins,  ctk_hidden  = collect_all("customtkinter")
pw_datas,      pw_bins,   pw_hidden   = collect_all("playwright")
rl_datas,      rl_bins,   rl_hidden   = collect_all("reportlab")
pil_datas,     pil_bins,  pil_hidden  = collect_all("PIL")

all_datas    = ctk_datas + pw_datas + rl_datas + pil_datas
all_binaries = ctk_bins  + pw_bins  + rl_bins  + pil_bins
all_hidden   = ctk_hidden + pw_hidden + rl_hidden + pil_hidden + [
    # Tkinter
    "tkinter", "tkinter.messagebox", "tkinter.filedialog",
    # Playwright
    "playwright", "playwright.sync_api", "playwright._impl",
    "playwright._impl._driver",
    # OpenAI
    "openai", "openai.types", "httpx", "anyio", "sniffio",
    # ReportLab
    "reportlab", "reportlab.lib", "reportlab.lib.styles",
    "reportlab.lib.enums", "reportlab.lib.units",
    "reportlab.lib.pagesizes", "reportlab.platypus",
    "reportlab.pdfbase", "reportlab.pdfbase.ttfonts",
    "reportlab.pdfbase.pdfmetrics",
    # Proje modülleri
    "utils", "utils.config",
    "services", "services.database", "services.openai_service",
    "services.pdf_service", "services.smtp_service", "services.telegram_service",
    "bot", "bot.browser", "bot.login", "bot.scraper", "bot.applicator", "bot.runner",
    "gui", "gui.app", "gui.login_tab", "gui.settings_tab",
    "gui.bot_tab", "gui.applications_tab", "gui.contacts_tab",
    # Stdlib
    "sqlite3", "_sqlite3", "queue", "threading", "webbrowser", "tempfile",
    "email", "email.mime", "email.mime.text",
]

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "numpy", "pandas", "scipy",
        "cv2",
        "IPython", "jupyter", "notebook",
        "test", "unittest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # onedir → binaries ayrı klasörde
    name="AusbildungBot",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                  # GUI uygulaması — konsol penceresi yok
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="icon.ico",              # İkon eklemek istersen: .ico dosyasını buraya yaz
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=["playwright*.exe", "*.node"],
    name="AusbildungBot",
)
