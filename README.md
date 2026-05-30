<div align="center">

**🌐 Language / Sprache / Dil:**
[🇬🇧 English](README.md) &nbsp;|&nbsp; [🇹🇷 Türkçe](README.tr.md) &nbsp;|&nbsp; [🇩🇪 Deutsch](README.de.md)

# 🎓 AusbildungBot

**Automated apprenticeship application bot for Ausbildung.de**

[![Release](https://img.shields.io/github/v/release/ck-cankurt/ausbildungbot?style=for-the-badge&color=5b2d8e)](https://github.com/ck-cankurt/ausbildungbot/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078d4?style=for-the-badge&logo=windows)](https://github.com/ck-cankurt/ausbildungbot/releases)
[![Powered by Ubden](https://img.shields.io/badge/Powered%20by-Ubden%20Open%20Source%20Community-9060c0?style=for-the-badge)](https://github.com/ubden)

<br/>

> A desktop application that automatically applies to apprenticeship listings (Ausbildungsplätze) on ausbildung.de.  
> Real browser control via Playwright · Personalised cover letters via OpenAI GPT-4o-mini · 3-language UI (TR / DE / EN)

<br/>

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Automatic Applications** | Finds all direct-apply listings and fills out the form automatically |
| 📝 **AI Cover Letter** | Generates a personal German *Kurz-Anschreiben* for each listing using GPT-4o-mini |
| 📄 **PDF Generation** | Creates a PDF *Anschreiben* and uploads it when required |
| 🔍 **Smart Filtering** | Filter by city, radius, sector, training type and keyword |
| 📬 **Contact Management** | Automatically extracts contact persons from listing pages |
| 📧 **Bulk Mail** | Sends templated e-mails to collected contacts (5 s interval) |
| 📱 **Telegram Notifications** | Sends a formatted Telegram message for every successful application |
| 📊 **Application Report** | Lists all applications by status, company and date |
| 🔒 **Local Storage** | All data stored in SQLite — nothing is sent to the cloud |
| 🌐 **3-Language UI** | Switch between Turkish, German and English without restarting manually |
| 🖥 **Modern GUI** | Dark-mode desktop interface built with customtkinter |

---

## 📸 Screenshots

<details>
<summary><b>🖼 Click to expand screenshots</b></summary>

<br/>

**Login Tab — Account credentials + Profile warning**
> *(Add `screenshots/login.png` here)*

**Bot Tab — Start, keyword filter, live log**
> *(Add `screenshots/bot.png` here)*

**Settings Tab — OpenAI, SMTP, Telegram, filters**
> *(Add `screenshots/settings.png` here)*

**Applications Tab — Table and statistics**
> *(Add `screenshots/applications.png` here)*

**Contacts Tab — Contact list and mail sending**
> *(Add `screenshots/contacts.png` here)*

</details>

---

## 🚀 Installation

### Option 1: Pre-built EXE (Recommended — Windows)

1. Download the latest release from the [Releases](https://github.com/ck-cankurt/ausbildungbot/releases/latest) page
2. Extract the ZIP file to a folder
3. Run `kurulum.bat` **as Administrator** — this downloads Chromium (~150 MB)
4. Run `AusbildungBot.exe`

```
AusbildungBot/
├── AusbildungBot.exe     ← Application
├── kurulum.bat           ← FIRST-TIME SETUP: downloads Chromium
├── playwright_browsers/  ← Created automatically by kurulum.bat
├── config.json           ← Settings (auto-created)
└── applications.db       ← Application database (auto-created)
```

---

### Option 2: Run from Source

**Requirements:** Python 3.11+, pip

```bash
# 1. Clone the repo
git clone https://github.com/ck-cankurt/ausbildungbot.git
cd ausbildungbot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browser
playwright install chromium

# 4. Launch
python main.py
```

---

## ⚙️ Configuration

The app creates `config.json` automatically on first launch. All settings are managed from the UI:

### Login Tab
- ausbildung.de e-mail and password

### Settings Tab

| Field | Description |
|-------|-------------|
| OpenAI API Key | `sk-…` format — required for GPT-4o-mini |
| City | Search city (e.g. Heidelberg) |
| Radius | 10 / 25 / 50 / 100 / 200 km |
| Sector | 25 sector options |
| Personal Info | Vorname, Nachname, address (for PDF) |
| SMTP Settings | SMTP server info for sending e-mail |
| Telegram Notifications | Bot token + Chat ID for application notifications |

### Bot Tab — Keyword Filter

```
🔍 Keyword Filter: [ kalt          ]
                   [ Kaufmann       ]
                   [ Informatik     ]
                   [ empty = all    ]
```

When a keyword is entered, the search URL becomes:
```
https://www.ausbildung.de/suche/?search=kalt|Mannheim&radius=50
```

---

## 🤖 How the Bot Works

```
Start Bot
  └─ Browser launches (Chromium)
  └─ Logs in to ausbildung.de
  └─ Scans listings (scroll + "Mehr Ergebnisse laden")
       └─ For each direct-apply listing:
            ├─ Already in DB? → skip
            ├─ Contact person saved (if found)
            ├─ "Bereits beworben" → already_applied
            ├─ Form completed (5 steps):
            │    ├─ Step 1: Personal data
            │    ├─ Step 2: Contact details
            │    ├─ Step 3: Zeugnisse (from profile)
            │    ├─ Step 4: Anschreiben (AI-generated + PDF upload)
            │    └─ Step 5: Files (from profile)
            ├─ Überprüfen → Bewerbung abschicken
            ├─ Verification: navigate back to listing page
            └─ Save to DB → notify GUI + Telegram (if enabled)
  └─ Done: Applied / Skipped / Error report
```

---

## 📧 SMTP Mail Setup (Gmail example)

1. Enable **2-step verification** on your Gmail account
2. Generate an app password at [App Passwords](https://myaccount.google.com/apppasswords)
3. Enter in the Settings tab:

```
SMTP Server:  smtp.gmail.com
SMTP Port:    587
Email:        example@gmail.com
Password:     xxxx xxxx xxxx xxxx  (app password)
STARTTLS:     ✅ enabled
```

---

## 📱 Telegram Notifications

Telegram notifications are optional and can be enabled from the Settings tab. When enabled, the bot sends one formatted message after each successful `applied` application.

1. Open Telegram and create a bot with [@BotFather](https://t.me/BotFather) using `/newbot`
2. Copy the API token into the **Bot API Token** field
3. Send any message to your new bot
4. Open [@userinfobot](https://t.me/userinfobot), send `/start`, and copy the `Id` value into **Chat ID**
5. Click **Send Test Message** in Settings to verify the connection

---

## 🔨 Build EXE from Source

```bash
pip install pyinstaller
pyinstaller ausbildung.spec --clean -y
```

Output: `dist/AusbildungBot/AusbildungBot.exe`

---

## 📁 Project Structure

```
ausbildungbot/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── ausbildung.spec            # PyInstaller config
├── kurulum.bat                # Chromium setup script
│
├── gui/                       # UI (customtkinter)
│   ├── app.py                 # Main window + tab manager
│   ├── login_tab.py           # Login + important note
│   ├── settings_tab.py        # Settings (OpenAI, filters, SMTP, Telegram)
│   ├── bot_tab.py             # Bot control + keyword filter + log
│   ├── applications_tab.py    # Application table + statistics
│   └── contacts_tab.py        # Contacts + bulk mail
│
├── bot/                       # Bot engine
│   ├── browser.py             # Playwright start/stop
│   ├── login.py               # ausbildung.de login flow
│   ├── scraper.py             # Listing scraper + URL builder
│   ├── applicator.py          # Form filling + submission
│   └── runner.py              # Bot workflow manager
│
├── services/                  # External services
│   ├── database.py            # SQLite CRUD (applications + contacts)
│   ├── openai_service.py      # GPT-4o-mini Anschreiben generator
│   ├── pdf_service.py         # ReportLab PDF generator
│   ├── smtp_service.py        # SMTP mail sender
│   └── telegram_service.py    # Telegram Bot API notifications
│
└── utils/
    ├── config.py              # config.json read/write
    └── i18n.py                # Translations (TR / DE / EN)
```

---

## ⚠️ Important Notes

- **Complete your profile first:** Make sure your ausbildung.de profile is fully filled in before starting the bot. CV, photo and documents must be uploaded.
- **OpenAI API Key:** Required for AI-generated cover letters. Without it, the bot leaves the Anschreiben field empty.
- **Legal responsibility:** This bot is designed to apply on behalf of the user with their own account. The user is responsible for the quality and accuracy of each application.
- **Rate limiting:** ausbildung.de may have bot protection. Applying too quickly can result in a temporary block.

---

## 🛠 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | ≥5.2.2 | Modern GUI framework |
| [playwright](https://playwright.dev/python/) | ≥1.44.0 | Browser automation |
| [openai](https://github.com/openai/openai-python) | ≥1.30.0 | AI cover letter generation |
| [reportlab](https://www.reportlab.com/) | ≥4.0.0 | PDF generation |
| [Pillow](https://python-pillow.org/) | ≥10.0.0 | Image processing (ReportLab dependency) |

---

## 🤝 Contributing

Pull requests and issues are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add new feature: ...'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📜 License

This project is licensed under the [MIT License](LICENSE). Free to use, modify and distribute.

---

<div align="center">

**Powered by [Ubden Open Source Community](https://github.com/ubden)**

[![GitHub](https://img.shields.io/badge/GitHub-ck--cankurt-181717?style=flat-square&logo=github)](https://github.com/ck-cankurt)
[![Donate](https://img.shields.io/badge/♥-Donate-ff69b4?style=flat-square)](https://ubd.one/donate)

*If you find this project useful, don't forget to leave a ⭐!*

</div>
