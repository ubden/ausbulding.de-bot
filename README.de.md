<div align="center">

**🌐 Language / Sprache / Dil:**
[🇬🇧 English](README.md) &nbsp;|&nbsp; [🇹🇷 Türkçe](README.tr.md) &nbsp;|&nbsp; [🇩🇪 Deutsch](README.de.md)

# 🎓 AusbildungBot

**Automatischer Bewerbungsbot für Ausbildung.de**

[![Release](https://img.shields.io/github/v/release/ck-cankurt/ausbildungbot?style=for-the-badge&color=5b2d8e)](https://github.com/ck-cankurt/ausbildungbot/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078d4?style=for-the-badge&logo=windows)](https://github.com/ck-cankurt/ausbildungbot/releases)
[![Powered by Ubden](https://img.shields.io/badge/Powered%20by-Ubden%20Open%20Source%20Community-9060c0?style=for-the-badge)](https://github.com/ubden)

<br/>

> Desktop-Anwendung, die automatisch Bewerbungen auf Ausbildungsplätze über ausbildung.de versendet.  
> Echte Browsersteuerung via Playwright · Persönliche Anschreiben via OpenAI GPT-4o-mini · 3-sprachige Oberfläche (TR / DE / EN)

<br/>

</div>

---

## ✨ Funktionen

| Funktion | Beschreibung |
|----------|-------------|
| 🤖 **Automatische Bewerbung** | Findet alle Direktbewerbungs-Stellen und füllt das Formular automatisch aus |
| 📝 **KI-Anschreiben** | Generiert für jede Stelle ein individuelles deutsches *Kurz-Anschreiben* (GPT-4o-mini) |
| 📄 **PDF-Erstellung** | Erstellt ein PDF-Anschreiben und lädt es hoch, wenn erforderlich |
| 🔍 **Intelligente Filter** | Filtern nach Stadt, Umkreis, Branche, Ausbildungsart und Stichwort |
| 📬 **Kontaktverwaltung** | Extrahiert automatisch Ansprechpersonen aus den Stellenanzeigen |
| 📧 **Massen-E-Mail** | Sendet Vorlagen-E-Mails an gesammelte Kontakte (5-Sekunden-Pause) |
| 📊 **Bewerbungsübersicht** | Listet alle Bewerbungen nach Status, Unternehmen und Datum auf |
| 🔒 **Lokale Speicherung** | Alle Daten werden in SQLite gespeichert — nichts geht in die Cloud |
| 🌐 **3-sprachige Oberfläche** | Zwischen Türkisch, Deutsch und Englisch jederzeit umschalten |
| 🖥 **Modernes GUI** | Dark-Mode Desktop-Oberfläche mit customtkinter |

---

## 📸 Screenshots

<details>
<summary><b>🖼 Klicken zum Anzeigen der Screenshots</b></summary>

<br/>

**Anmeldung-Tab — Zugangsdaten + Profilhinweis**
> *(Hier `screenshots/login.png` einfügen)*

**Bot-Tab — Start, Stichwortfilter, Live-Log**
> *(Hier `screenshots/bot.png` einfügen)*

**Einstellungen-Tab — OpenAI, SMTP, Filter**
> *(Hier `screenshots/settings.png` einfügen)*

**Bewerbungen-Tab — Tabelle und Statistiken**
> *(Hier `screenshots/applications.png` einfügen)*

**Kontakte-Tab — Kontaktliste und E-Mail-Versand**
> *(Hier `screenshots/contacts.png` einfügen)*

</details>

---

## 🚀 Installation

### Option 1: Fertige EXE (Empfohlen — Windows)

1. Lade die neueste Version von der [Releases](https://github.com/ck-cankurt/ausbildungbot/releases/latest)-Seite herunter
2. Entpacke die ZIP-Datei in einen Ordner
3. Führe `kurulum.bat` **als Administrator** aus — lädt Chromium herunter (~150 MB)
4. Starte `AusbildungBot.exe`

```
AusbildungBot/
├── AusbildungBot.exe     ← Anwendung
├── kurulum.bat           ← ERSTEINRICHTUNG: lädt Chromium herunter
├── playwright_browsers/  ← Wird automatisch durch kurulum.bat erstellt
├── config.json           ← Einstellungen (automatisch erstellt)
└── applications.db       ← Bewerbungsdatenbank (automatisch erstellt)
```

---

### Option 2: Aus dem Quellcode starten

**Voraussetzungen:** Python 3.11+, pip

```bash
# 1. Repository klonen
git clone https://github.com/ck-cankurt/ausbildungbot.git
cd ausbildungbot

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Playwright-Browser installieren
playwright install chromium

# 4. Anwendung starten
python main.py
```

---

## ⚙️ Konfiguration

Die Anwendung erstellt beim ersten Start automatisch eine `config.json`. Alle Einstellungen werden über die Oberfläche vorgenommen:

### Anmeldung-Tab
- ausbildung.de E-Mail und Passwort

### Einstellungen-Tab

| Feld | Beschreibung |
|------|-------------|
| OpenAI API Key | Format `sk-…` — erforderlich für GPT-4o-mini |
| Stadt | Suchstadt (z. B. Heidelberg) |
| Umkreis | 10 / 25 / 50 / 100 / 200 km |
| Branche | 25 Branchenoptionen |
| Persönliche Daten | Vorname, Nachname, Adresse (für PDF) |
| SMTP-Einstellungen | SMTP-Serverdaten für den E-Mail-Versand |

### Bot-Tab — Stichwortfilter

```
🔍 Stichwortfilter: [ kalt          ]
                    [ Kaufmann       ]
                    [ Informatik     ]
                    [ leer = alle   ]
```

Bei einem eingegebenen Stichwort sieht die Such-URL so aus:
```
https://www.ausbildung.de/suche/?search=kalt|Mannheim&radius=50
```

---

## 🤖 Wie der Bot funktioniert

```
Bot starten
  └─ Browser öffnet sich (Chromium)
  └─ Anmeldung bei ausbildung.de
  └─ Stellen werden gescannt (Scrollen + "Mehr Ergebnisse laden")
       └─ Für jede Direktbewerbungsstelle:
            ├─ Bereits in DB? → überspringen
            ├─ Kontaktperson speichern (falls vorhanden)
            ├─ "Bereits beworben" → already_applied
            ├─ Formular ausfüllen (5 Schritte):
            │    ├─ Schritt 1: Persönliche Daten
            │    ├─ Schritt 2: Kontaktdaten
            │    ├─ Schritt 3: Zeugnisse (aus Profil)
            │    ├─ Schritt 4: Anschreiben (KI-generiert + PDF-Upload)
            │    └─ Schritt 5: Dateien (aus Profil)
            ├─ Überprüfen → Bewerbung abschicken
            ├─ Verifizierung: zur Stellenanzeige zurücknavigieren
            └─ In DB speichern → GUI benachrichtigen
  └─ Fertig: Beworben / Übersprungen / Fehlerbericht
```

---

## 📧 SMTP E-Mail-Einrichtung (Gmail-Beispiel)

1. Aktiviere die **2-Schritt-Verifizierung** in deinem Gmail-Konto
2. Erstelle ein App-Passwort unter [App-Passwörter](https://myaccount.google.com/apppasswords)
3. Trage die Daten im Einstellungen-Tab ein:

```
SMTP-Server:  smtp.gmail.com
SMTP-Port:    587
E-Mail:       beispiel@gmail.com
Passwort:     xxxx xxxx xxxx xxxx  (App-Passwort)
STARTTLS:     ✅ aktiviert
```

---

## 🔨 EXE aus Quellcode bauen

```bash
pip install pyinstaller
pyinstaller ausbildung.spec --clean -y
```

Ausgabe: `dist/AusbildungBot/AusbildungBot.exe`

---

## 📁 Projektstruktur

```
ausbildungbot/
├── main.py                    # Einstiegspunkt
├── requirements.txt           # Python-Abhängigkeiten
├── ausbildung.spec            # PyInstaller-Konfiguration
├── kurulum.bat                # Chromium-Installationsskript
│
├── gui/                       # Benutzeroberfläche (customtkinter)
│   ├── app.py                 # Hauptfenster + Tab-Verwaltung
│   ├── login_tab.py           # Anmeldung + Wichtiger Hinweis
│   ├── settings_tab.py        # Einstellungen (OpenAI, Filter, SMTP)
│   ├── bot_tab.py             # Bot-Steuerung + Stichwortfilter + Log
│   ├── applications_tab.py    # Bewerbungstabelle + Statistiken
│   └── contacts_tab.py        # Kontakte + Massen-E-Mail
│
├── bot/                       # Bot-Engine
│   ├── browser.py             # Playwright Start/Stop
│   ├── login.py               # ausbildung.de Anmeldungsablauf
│   ├── scraper.py             # Stellen-Scraper + URL-Builder
│   ├── applicator.py          # Formular ausfüllen + Absenden
│   └── runner.py              # Bot-Workflow-Manager
│
├── services/                  # Externe Dienste
│   ├── database.py            # SQLite CRUD (applications + contacts)
│   ├── openai_service.py      # GPT-4o-mini Anschreiben-Generator
│   ├── pdf_service.py         # ReportLab PDF-Generator
│   └── smtp_service.py        # SMTP E-Mail-Versand
│
└── utils/
    ├── config.py              # config.json lesen/schreiben
    └── i18n.py                # Übersetzungen (TR / DE / EN)
```

---

## ⚠️ Wichtige Hinweise

- **Profil vollständig ausfüllen:** Stelle sicher, dass dein ausbildung.de-Profil vollständig ausgefüllt ist, bevor du den Bot startest. Lebenslauf, Foto und Zeugnisse müssen hochgeladen sein.
- **OpenAI API Key:** Für KI-generierte Anschreiben erforderlich. Ohne Key lässt der Bot das Anschreiben-Feld leer.
- **Rechtliche Verantwortung:** Dieser Bot wurde entwickelt, damit Nutzer im eigenen Namen mit ihrem eigenen Konto Bewerbungen versenden. Der Nutzer ist für die Qualität und Richtigkeit jeder Bewerbung verantwortlich.
- **Rate-Limiting:** ausbildung.de verfügt möglicherweise über Bot-Schutz. Zu schnell gesendete Bewerbungen können zu einer vorübergehenden Sperre führen.

---

## 🛠 Abhängigkeiten

| Paket | Version | Verwendung |
|-------|---------|-----------|
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | ≥5.2.2 | Modernes GUI-Framework |
| [playwright](https://playwright.dev/python/) | ≥1.44.0 | Browser-Automatisierung |
| [openai](https://github.com/openai/openai-python) | ≥1.30.0 | KI-Anschreiben-Generierung |
| [reportlab](https://www.reportlab.com/) | ≥4.0.0 | PDF-Erstellung |
| [Pillow](https://python-pillow.org/) | ≥10.0.0 | Bildverarbeitung (ReportLab-Abhängigkeit) |

---

## 🤝 Mitwirken

Pull Requests und Issues sind herzlich willkommen!

1. Repository forken
2. Feature-Branch erstellen: `git checkout -b feature/meine-funktion`
3. Committen: `git commit -m 'Neue Funktion: ...'`
4. Pushen: `git push origin feature/meine-funktion`
5. Pull Request öffnen

---

## 📜 Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE). Frei verwendbar, veränderbar und verteilbar.

---

<div align="center">

**Powered by [Ubden Open Source Community](https://github.com/ubden)**

[![GitHub](https://img.shields.io/badge/GitHub-ck--cankurt-181717?style=flat-square&logo=github)](https://github.com/ck-cankurt)
[![Spenden](https://img.shields.io/badge/♥-Spenden-ff69b4?style=flat-square)](https://ubd.one/donate)

*Wenn dir das Projekt gefällt, hinterlasse bitte einen ⭐!*

</div>
