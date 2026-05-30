"""
Çok dilli destek (TR / DE / EN).
Kullanım:
    from utils.i18n import t, set_lang, LANG_OPTIONS
    t("BOT_START")   → aktif dilde karşılık
"""

from __future__ import annotations

_current: str = "tr"

LANG_OPTIONS = {
    "tr": "Türkçe",
    "de": "Deutsch",
    "en": "English",
}

# ─────────────────────────────────────────────────────────────────────────────
# Çeviri tablosu
# ─────────────────────────────────────────────────────────────────────────────
_T: dict[str, dict[str, str]] = {

    # ── Uygulama geneli ──────────────────────────────────────────────────────
    "APP_TITLE":           {"tr": "Ausbildung.de Başvuru Botu",        "de": "Ausbildung.de Bewerbungsbot",          "en": "Ausbildung.de Application Bot"},
    "APP_SUBTITLE":        {"tr": "Otomatik Başvuru Sistemi",           "de": "Automatisches Bewerbungssystem",       "en": "Automatic Application System"},
    "TAB_LOGIN":           {"tr": "Giriş",                              "de": "Anmeldung",                           "en": "Login"},
    "TAB_SETTINGS":        {"tr": "Ayarlar",                            "de": "Einstellungen",                       "en": "Settings"},
    "TAB_BOT":             {"tr": "Bot",                                "de": "Bot",                                 "en": "Bot"},
    "TAB_APPLICATIONS":    {"tr": "Başvurular",                         "de": "Bewerbungen",                         "en": "Applications"},
    "TAB_CONTACTS":        {"tr": "Kontaktlar",                         "de": "Kontakte",                            "en": "Contacts"},
    "FOOTER_POWERED_BY":   {"tr": "Powered by",                         "de": "Powered by",                          "en": "Powered by"},
    "FOOTER_COMMUNITY":    {"tr": "Ubden Open Source Community",        "de": "Ubden Open Source Community",         "en": "Ubden Open Source Community"},
    "FOOTER_VERSION":      {"tr": "AusbildungBot v2.0",                 "de": "AusbildungBot v2.0",                  "en": "AusbildungBot v2.0"},
    "FOOTER_DONATE":       {"tr": "♥ Bağış Yap",                       "de": "♥ Spenden",                           "en": "♥ Donate"},
    "LANG_LABEL":          {"tr": "🌐 Dil:",                            "de": "🌐 Sprache:",                         "en": "🌐 Language:"},

    # ── Giriş sekmesi ────────────────────────────────────────────────────────
    "LOGIN_HEADER":        {"tr": "🔐  Ausbildung.de Hesap Girişi",     "de": "🔐  Ausbildung.de Anmeldung",         "en": "🔐  Ausbildung.de Account Login"},
    "LOGIN_EMAIL":         {"tr": "E-posta:",                           "de": "E-Mail:",                             "en": "Email:"},
    "LOGIN_EMAIL_PH":      {"tr": "ornek@email.com",                   "de": "beispiel@email.com",                  "en": "example@email.com"},
    "LOGIN_PASSWORD":      {"tr": "Şifre:",                            "de": "Passwort:",                           "en": "Password:"},
    "LOGIN_PASS_PH":       {"tr": "Şifreniz",                          "de": "Ihr Passwort",                        "en": "Your password"},
    "LOGIN_SHOW_PASS":     {"tr": "Şifreyi göster",                    "de": "Passwort anzeigen",                   "en": "Show password"},
    "LOGIN_SAVE":          {"tr": "Kaydet",                             "de": "Speichern",                           "en": "Save"},
    "LOGIN_SAVED":         {"tr": "✓ Kaydedildi!",                     "de": "✓ Gespeichert!",                      "en": "✓ Saved!"},
    "LOGIN_INFO":          {"tr": "Bilgiler yerel config.json dosyasına kaydedilir.",
                            "de": "Daten werden lokal in config.json gespeichert.",
                            "en": "Credentials are saved locally in config.json."},
    "LOGIN_NOTE_TITLE":    {"tr": "⚠️  Önemli Not — Botu Başlatmadan Önce Okuyun",
                            "de": "⚠️  Wichtiger Hinweis — Vor dem Start lesen",
                            "en": "⚠️  Important — Read Before Starting the Bot"},
    "LOGIN_NOTE_BODY":     {
        "tr": (
            "Botu başlatmadan önce ausbildung.de profilinizin eksiksiz ve güncel olması\n"
            "zorunludur. Eksik profille bot başvuruları tamamlayamaz.\n\n"
            "Lütfen başlatmadan önce şunların tamamlandığından emin olun:\n"
            "  ✅  Güncel CV (Lebenslauf) sisteme yüklü\n"
            "  ✅  Ön yazı (Anschreiben) veya profil metni dolu\n"
            "  ✅  Kişisel bilgiler (ad, adres, okul bilgileri) eksiksiz\n"
            "  ✅  Fotoğraf ve sertifikalar (varsa) yüklü"
        ),
        "de": (
            "Bevor du den Bot startest, muss dein ausbildung.de-Profil vollständig\n"
            "und aktuell sein. Mit einem unvollständigen Profil kann der Bot\n"
            "Bewerbungen nicht korrekt abschicken.\n\n"
            "Bitte stelle sicher, dass folgende Punkte erledigt sind:\n"
            "  ✅  Aktueller Lebenslauf hochgeladen\n"
            "  ✅  Anschreiben oder Profiltext ausgefüllt\n"
            "  ✅  Persönliche Daten (Name, Adresse, Schulinfos) vollständig\n"
            "  ✅  Foto und Zeugnisse (falls vorhanden) hochgeladen"
        ),
        "en": (
            "Before starting the bot, your ausbildung.de profile must be complete\n"
            "and up to date. An incomplete profile means the bot cannot submit\n"
            "applications correctly.\n\n"
            "Please make sure all of the following are done:\n"
            "  ✅  Up-to-date CV (Lebenslauf) uploaded\n"
            "  ✅  Cover letter (Anschreiben) or profile text filled in\n"
            "  ✅  Personal data (name, address, school info) complete\n"
            "  ✅  Photo and certificates (if any) uploaded"
        ),
    },
    "LOGIN_PROFILE_LINK":  {"tr": "  🔗  Profilinize gitmek için buraya tıklayın  ",
                            "de": "  🔗  Hier klicken, um zum Profil zu gelangen  ",
                            "en": "  🔗  Click here to go to your profile  "},

    # ── Ayarlar sekmesi ──────────────────────────────────────────────────────
    "SETTINGS_LANG_SECTION":  {"tr": "Dil / Language / Sprache",       "de": "Sprache / Dil / Language",            "en": "Language / Sprache / Dil"},
    "SETTINGS_LANG_RESTART":  {"tr": "Dil değişikliği — uygulama yeniden başlatılıyor...",
                               "de": "Sprache geändert — App wird neu gestartet...",
                               "en": "Language changed — restarting app..."},
    "SETTINGS_OPENAI":        {"tr": "ChatGPT / OpenAI Ayarları",      "de": "ChatGPT / OpenAI Einstellungen",      "en": "ChatGPT / OpenAI Settings"},
    "SETTINGS_OPENAI_KEY":    {"tr": "OpenAI API Key:",                "de": "OpenAI API-Schlüssel:",               "en": "OpenAI API Key:"},
    "SETTINGS_OPENAI_BG":     {"tr": "Arka Plan Bilgisi:",             "de": "Hintergrundinformation:",             "en": "Background Info:"},
    "SETTINGS_OPENAI_BG_HINT":{"tr": "(Anschreiben için ek bağlam — ör: ilgi alanları, dil bilgisi)",
                               "de": "(Zusätzlicher Kontext für das Anschreiben — z.B. Interessen, Sprachkenntnisse)",
                               "en": "(Extra context for the cover letter — e.g. interests, language skills)"},
    "SETTINGS_SHOW_KEY":      {"tr": "API Key'i göster",               "de": "API-Schlüssel anzeigen",              "en": "Show API Key"},
    "SETTINGS_SEARCH":        {"tr": "Arama Ayarları",                 "de": "Sucheinstellungen",                   "en": "Search Settings"},
    "SETTINGS_CITY":          {"tr": "Şehir:",                         "de": "Stadt:",                              "en": "City:"},
    "SETTINGS_CITY_PH":       {"tr": "ör: Heidelberg",                 "de": "z.B.: Heidelberg",                    "en": "e.g.: Heidelberg"},
    "SETTINGS_RADIUS":        {"tr": "Yarıçap (km):",                  "de": "Umkreis (km):",                       "en": "Radius (km):"},
    "SETTINGS_FILTERS":       {"tr": "Filtreler (isteğe bağlı)",       "de": "Filter (optional)",                   "en": "Filters (optional)"},
    "SETTINGS_ART":           {"tr": "Ausbildungsart:",                "de": "Ausbildungsart:",                     "en": "Training type:"},
    "SETTINGS_ABSCHLUSS":     {"tr": "Abschluss:",                     "de": "Abschluss:",                         "en": "Qualification:"},
    "SETTINGS_BRANCHE":       {"tr": "Branche:",                       "de": "Branche:",                            "en": "Sector:"},
    "SETTINGS_SKIP_PDF":      {"tr": "PDF Anschreiben gerektiren ilanları atla\n(sadece metin Kurz-Anschreiben kabul eden ilanlara başvur)",
                               "de": "Stellen mit PDF-Anschreiben überspringen\n(nur Stellen mit Kurz-Anschreiben bewerben)",
                               "en": "Skip listings requiring a PDF cover letter\n(only apply to listings accepting a short text cover letter)"},
    "SETTINGS_PERSONAL":      {"tr": "Kişisel Bilgiler (PDF Anschreiben için)",
                               "de": "Persönliche Daten (für PDF-Anschreiben)",
                               "en": "Personal Details (for PDF cover letter)"},
    "SETTINGS_VORNAME":       {"tr": "Vorname:",                       "de": "Vorname:",                            "en": "First name:"},
    "SETTINGS_NACHNAME":      {"tr": "Nachname:",                      "de": "Nachname:",                           "en": "Last name:"},
    "SETTINGS_STRASSE":       {"tr": "Straße + Nr:",                   "de": "Straße + Nr:",                        "en": "Street + No:"},
    "SETTINGS_PLZ":           {"tr": "PLZ:",                           "de": "PLZ:",                                "en": "Postcode:"},
    "SETTINGS_STADT":         {"tr": "Stadt (Wohnsitz):",              "de": "Wohnort:",                            "en": "City (residence):"},
    "SETTINGS_SMTP":          {"tr": "E-posta / SMTP Ayarları",        "de": "E-Mail / SMTP-Einstellungen",         "en": "Email / SMTP Settings"},
    "SETTINGS_SMTP_HOST":     {"tr": "SMTP Sunucu:",                   "de": "SMTP-Server:",                        "en": "SMTP Server:"},
    "SETTINGS_SMTP_PORT":     {"tr": "SMTP Port:",                     "de": "SMTP-Port:",                          "en": "SMTP Port:"},
    "SETTINGS_SMTP_EMAIL":    {"tr": "Gönderen E-posta:",              "de": "Absender-E-Mail:",                    "en": "Sender Email:"},
    "SETTINGS_SMTP_PASS":     {"tr": "SMTP Şifre:",                    "de": "SMTP-Passwort:",                      "en": "SMTP Password:"},
    "SETTINGS_SMTP_SHOW":     {"tr": "SMTP şifresini göster",          "de": "SMTP-Passwort anzeigen",              "en": "Show SMTP password"},
    "SETTINGS_SMTP_TLS":      {"tr": "STARTTLS kullan (port 587 için önerilir)",
                               "de": "STARTTLS verwenden (empfohlen für Port 587)",
                               "en": "Use STARTTLS (recommended for port 587)"},
    "SETTINGS_SMTP_TEST":     {"tr": "Bağlantıyı Test Et",             "de": "Verbindung testen",                   "en": "Test Connection"},
    "SETTINGS_SMTP_TESTING":  {"tr": "Test ediliyor...",               "de": "Teste Verbindung...",                 "en": "Testing connection..."},
    "SETTINGS_SMTP_OK":       {"tr": "Bağlantı başarılı! Test maili gönderildi.",
                               "de": "Verbindung erfolgreich! Test-E-Mail gesendet.",
                               "en": "Connection successful! Test email sent."},
    "SETTINGS_SMTP_ERR":      {"tr": "Hata:",                          "de": "Fehler:",                             "en": "Error:"},
    "SETTINGS_BROWSER":       {"tr": "Tarayıcı",                       "de": "Browser",                             "en": "Browser"},
    "SETTINGS_HEADLESS":      {"tr": "Arka planda çalıştır (headless mod — tarayıcı görünmez)",
                               "de": "Im Hintergrund ausführen (Headless-Modus — kein Browserfenster)",
                               "en": "Run in background (headless mode — no browser window)"},
    "SETTINGS_SAVE":          {"tr": "💾  Ayarları Kaydet",            "de": "💾  Einstellungen speichern",         "en": "💾  Save Settings"},
    "SETTINGS_SAVED":         {"tr": "✓ Kaydedildi!",                  "de": "✓ Gespeichert!",                      "en": "✓ Saved!"},

    # ── Bot sekmesi ──────────────────────────────────────────────────────────
    "BOT_HEADER":             {"tr": "🤖  Bot Kontrolü",               "de": "🤖  Bot-Steuerung",                   "en": "🤖  Bot Controls"},
    "BOT_START":              {"tr": "▶  Bot Başlat",                  "de": "▶  Bot starten",                      "en": "▶  Start Bot"},
    "BOT_STOP":               {"tr": "⏹  Durdur",                     "de": "⏹  Stoppen",                         "en": "⏹  Stop"},
    "BOT_CLEAR_LOG":          {"tr": "🗑  Logu Temizle",               "de": "🗑  Log leeren",                      "en": "🗑  Clear Log"},
    "BOT_KEYWORD_LABEL":      {"tr": "🔍  Kelime Filtresi:",           "de": "🔍  Schlüsselwort-Filter:",           "en": "🔍  Keyword Filter:"},
    "BOT_KEYWORD_PH":         {"tr": "ör: Kaufmann, kalt, Informatik  (boş = tümü)",
                               "de": "z.B.: Kaufmann, kalt, Informatik  (leer = alle)",
                               "en": "e.g.: Kaufmann, kalt, Informatik  (empty = all)"},
    "BOT_KEYWORD_HINT":       {"tr": "Meslek adı, pozisyon veya okul türü yazın.\nBoş bırakılırsa tüm ilanlar taranır.",
                               "de": "Berufsbezeichnung, Position oder Schulart eingeben.\nLeer lassen = alle Stellen werden gescannt.",
                               "en": "Enter a job title, position or school type.\nLeave empty to scan all listings."},
    "BOT_STATUS_LABEL":       {"tr": "Durum:",                         "de": "Status:",                             "en": "Status:"},
    "BOT_STATUS_WAITING":     {"tr": "Bekleniyor",                     "de": "Warten",                              "en": "Waiting"},
    "BOT_LOG_HEADER":         {"tr": "📋  Canlı Log",                  "de": "📋  Live-Log",                        "en": "📋  Live Log"},
    "BOT_STARTING":           {"tr": "Başlatılıyor...",                "de": "Wird gestartet...",                   "en": "Starting..."},
    "BOT_STOPPING":           {"tr": "Durduruluyor...",                "de": "Wird gestoppt...",                    "en": "Stopping..."},

    # ── Runner / log mesajları ───────────────────────────────────────────────
    "RUNNER_NO_CREDS":        {"tr": "HATA: E-posta ve şifre girilmemiş! Giriş sekmesini doldurun.",
                               "de": "FEHLER: E-Mail und Passwort fehlen! Bitte Anmeldedaten eingeben.",
                               "en": "ERROR: Email and password not set! Please fill in the Login tab."},
    "RUNNER_BROWSER_START":   {"tr": "Tarayıcı başlatılıyor...",       "de": "Browser wird gestartet...",           "en": "Starting browser..."},
    "RUNNER_BROWSER_ERR":     {"tr": "Tarayıcı başlatma hatası:",      "de": "Fehler beim Starten des Browsers:",   "en": "Browser start error:"},
    "RUNNER_LOGGING_IN":      {"tr": "Giriş yapılıyor...",             "de": "Anmeldung läuft...",                  "en": "Logging in..."},
    "RUNNER_LOGIN_FAIL":      {"tr": "Giriş başarısız",                "de": "Anmeldung fehlgeschlagen",            "en": "Login failed"},
    "RUNNER_SCANNING":        {"tr": "İlanlar taranıyor...",           "de": "Stellen werden gescannt...",          "en": "Scanning listings..."},
    "RUNNER_NO_JOBS":         {"tr": "Direkt başvuru ilanı bulunamadı.",
                               "de": "Keine Direktbewerbungsstellen gefunden.",
                               "en": "No direct application listings found."},
    "RUNNER_NO_JOBS_STATUS":  {"tr": "İlan bulunamadı",                "de": "Keine Stellen gefunden",              "en": "No listings found"},
    "RUNNER_SKIPPED_DB":      {"tr": "Atlandı (DB'de var):",           "de": "Übersprungen (bereits in DB):",       "en": "Skipped (already in DB):"},
    "RUNNER_APPLYING":        {"tr": "Başvuruluyor:",                  "de": "Bewerbung läuft:",                    "en": "Applying:"},
    "RUNNER_BOT_ERR":         {"tr": "Bot hatası:",                    "de": "Bot-Fehler:",                         "en": "Bot error:"},
    "RUNNER_STOPPING":        {"tr": "Durdurma sinyali gönderildi...", "de": "Stoppsignal gesendet...",             "en": "Stop signal sent..."},
    "RUNNER_ERROR_STATUS":    {"tr": "Hata",                           "de": "Fehler",                              "en": "Error"},
    "RUNNER_STOPPED":         {"tr": "Durduruldu",                     "de": "Gestoppt",                            "en": "Stopped"},
    "RUNNER_DONE":            {"tr": "Tamamlandı",                     "de": "Abgeschlossen",                       "en": "Done"},
    "RUNNER_APPLIED":         {"tr": "Başvurulan:",                    "de": "Beworben:",                           "en": "Applied:"},
    "RUNNER_SKIPPED":         {"tr": "Atlanan:",                       "de": "Übersprungen:",                       "en": "Skipped:"},
    "RUNNER_ERRORS":          {"tr": "Hata:",                          "de": "Fehler:",                             "en": "Errors:"},

    # ── Başvurular sekmesi ───────────────────────────────────────────────────
    "APPS_HEADER":            {"tr": "📋  Başvurular",                 "de": "📋  Bewerbungen",                     "en": "📋  Applications"},
    "APPS_REFRESH":           {"tr": "🔄  Yenile",                     "de": "🔄  Aktualisieren",                   "en": "🔄  Refresh"},
    "APPS_CLEAR_DB":          {"tr": "🗑  DB Temizle",                 "de": "🗑  DB leeren",                       "en": "🗑  Clear DB"},
    "APPS_COL_IDX":           {"tr": "#",                              "de": "#",                                   "en": "#"},
    "APPS_COL_POSITION":      {"tr": "Pozisyon",                       "de": "Position",                            "en": "Position"},
    "APPS_COL_COMPANY":       {"tr": "Şirket",                         "de": "Unternehmen",                         "en": "Company"},
    "APPS_COL_LOCATION":      {"tr": "Konum",                          "de": "Ort",                                 "en": "Location"},
    "APPS_COL_STATUS":        {"tr": "Durum",                          "de": "Status",                              "en": "Status"},
    "APPS_COL_DATE":          {"tr": "Tarih",                          "de": "Datum",                               "en": "Date"},
    "APPS_S_APPLIED":         {"tr": "Başvuruldu",                     "de": "Beworben",                            "en": "Applied"},
    "APPS_S_ALREADY":         {"tr": "Zaten Başvurulmuş",              "de": "Bereits beworben",                    "en": "Already Applied"},
    "APPS_S_SKIPPED":         {"tr": "Atlandı",                        "de": "Übersprungen",                        "en": "Skipped"},
    "APPS_S_ERROR":           {"tr": "Hata",                           "de": "Fehler",                              "en": "Error"},
    "APPS_S_PENDING":         {"tr": "Beklemede",                      "de": "Ausstehend",                          "en": "Pending"},
    "APPS_EMPTY":             {"tr": "Henüz başvuru kaydı yok.",       "de": "Noch keine Bewerbungen vorhanden.",    "en": "No application records yet."},
    "APPS_LOAD_MORE":         {"tr": "Daha fazla yükle",               "de": "Mehr laden",                           "en": "Load more"},
    "APPS_LOADED_COUNT":      {"tr": "{loaded} / {total} kayıt gösteriliyor",
                               "de": "{loaded} / {total} Einträge werden angezeigt",
                               "en": "Showing {loaded} / {total} records"},
    "APPS_PDF_BTN":           {"tr": "📄",                             "de": "📄",                                  "en": "📄"},
    "APPS_PDF_TITLE":         {"tr": "Anschreiben Önizleme",           "de": "Anschreiben Vorschau",                "en": "Anschreiben Preview"},
    "APPS_PDF_OPEN_SYS":      {"tr": "🖨  Sistemde Aç",               "de": "🖨  Im System öffnen",               "en": "🖨  Open in System"},
    "APPS_PDF_CLOSE":         {"tr": "✕  Kapat",                      "de": "✕  Schließen",                       "en": "✕  Close"},
    "APPS_PDF_NO_FITZ":       {"tr": "PyMuPDF kurulu değil.\nPDF önizleme için: pip install PyMuPDF",
                               "de": "PyMuPDF nicht installiert.\nFür die Vorschau: pip install PyMuPDF",
                               "en": "PyMuPDF not installed.\nFor preview: pip install PyMuPDF"},
    "APPS_PDF_LOAD_ERR":      {"tr": "PDF yüklenemedi:",               "de": "PDF konnte nicht geladen werden:",   "en": "PDF could not be loaded:"},
    "APPS_PDF_OPEN_BTN":      {"tr": "📂  PDF'i Aç",                  "de": "📂  PDF öffnen",                     "en": "📂  Open PDF"},
    "APPS_COL_PDF":           {"tr": "PDF",                            "de": "PDF",                                "en": "PDF"},
    "APPS_CONFIRM_TITLE":     {"tr": "Onayla",                         "de": "Bestätigen",                          "en": "Confirm"},
    "APPS_CONFIRM_MSG":       {"tr": "Tüm başvuru kayıtları silinecek.\nDevam etmek istiyor musunuz?",
                               "de": "Alle Bewerbungsdaten werden gelöscht.\nMöchtest du fortfahren?",
                               "en": "All application records will be deleted.\nDo you want to continue?"},
    "APPS_CLEARED_TITLE":     {"tr": "Temizlendi",                     "de": "Geleert",                             "en": "Cleared"},
    "APPS_CLEARED_MSG":       {"tr": "kayıt silindi.",                 "de": "Einträge gelöscht.",                  "en": "records deleted."},

    # ── Telegram ────────────────────────────────────────────────────────────
    "SETTINGS_TELEGRAM":      {"tr": "Telegram Bot Bildirimleri",       "de": "Telegram-Bot-Benachrichtigungen",     "en": "Telegram Bot Notifications"},
    "SETTINGS_TG_ENABLE":     {"tr": "Telegram bildirimlerini etkinleştir (başvurulan her pozisyon için mesaj gönderir)",
                               "de": "Telegram-Benachrichtigungen aktivieren (Nachricht bei jeder Bewerbung)",
                               "en": "Enable Telegram notifications (sends a message for every applied position)"},
    "SETTINGS_TG_TOKEN":      {"tr": "Bot API Token:",                  "de": "Bot-API-Token:",                      "en": "Bot API Token:"},
    "SETTINGS_TG_CHAT_ID":    {"tr": "Chat ID:",                        "de": "Chat-ID:",                            "en": "Chat ID:"},
    "SETTINGS_TG_SHOW":       {"tr": "Token'i göster",                  "de": "Token anzeigen",                      "en": "Show token"},
    "SETTINGS_TG_TEST":       {"tr": "📨  Test Mesajı Gönder",          "de": "📨  Testnachricht senden",            "en": "📨  Send Test Message"},
    "SETTINGS_TG_TESTING":    {"tr": "Gönderiliyor...",                 "de": "Wird gesendet...",                    "en": "Sending..."},
    "SETTINGS_TG_OK":         {"tr": "✓ Mesaj gönderildi!",             "de": "✓ Nachricht gesendet!",               "en": "✓ Message sent!"},
    "SETTINGS_TG_ERR":        {"tr": "Hata:",                           "de": "Fehler:",                             "en": "Error:"},
    "SETTINGS_TG_HOW_TITLE":  {"tr": "📱  Nasıl kurulur?",              "de": "📱  Einrichtungsanleitung",           "en": "📱  Setup Guide"},
    "SETTINGS_TG_HOW_BODY":   {
        "tr": (
            "① BOT TOKEN almak için:\n"
            "   • Telegram'da @BotFather'ı aç ve /newbot yaz\n"
            "   • Bot adı + kullanıcı adı gir\n"
            "   • Verilen token'i yukarıdaki alana yapıştır\n\n"
            "② CHAT ID almak için:\n"
            "   • Oluşturduğun bota bir mesaj gönder\n"
            "   • Telegram'da @userinfobot'a /start yaz\n"
            "   • Gelen 'Id:' değerini Chat ID alanına gir\n\n"
            "③ 'Test Mesajı Gönder' ile bağlantıyı doğrula"
        ),
        "de": (
            "① BOT TOKEN holen:\n"
            "   • Öffne @BotFather in Telegram und schreibe /newbot\n"
            "   • Bot-Name + Benutzername eingeben\n"
            "   • Den erhaltenen Token oben einfügen\n\n"
            "② CHAT ID holen:\n"
            "   • Sende deinem Bot eine Nachricht\n"
            "   • Schreibe @userinfobot /start in Telegram\n"
            "   • Den 'Id:'-Wert als Chat-ID eintragen\n\n"
            "③ Mit 'Testnachricht senden' die Verbindung prüfen"
        ),
        "en": (
            "① Get a BOT TOKEN:\n"
            "   • Open @BotFather in Telegram and send /newbot\n"
            "   • Enter a bot name + username\n"
            "   • Paste the token you receive into the field above\n\n"
            "② Get your CHAT ID:\n"
            "   • Send your new bot any message\n"
            "   • Open @userinfobot in Telegram and send /start\n"
            "   • Copy the 'Id:' value into the Chat ID field\n\n"
            "③ Click 'Send Test Message' to verify the connection"
        ),
    },

    # ── Kontaktlar sekmesi ───────────────────────────────────────────────────
    "CON_HEADER":             {"tr": "📬  Kontakt Kişiler & Toplu Mail","de": "📬  Kontaktpersonen & Massen-E-Mail", "en": "📬  Contact Persons & Bulk Mail"},
    "CON_REFRESH":            {"tr": "🔄  Yenile",                     "de": "🔄  Aktualisieren",                   "en": "🔄  Refresh"},
    "CON_SEND_ALL":           {"tr": "📧  Tümüne Mail Gönder",         "de": "📧  An alle senden",                  "en": "📧  Send to All"},
    "CON_SEND_UNSENT":        {"tr": "✉  Gönderilenler Hariç Gönder", "de": "✉  Noch nicht Gesendet senden",       "en": "✉  Send to Unsent"},
    "CON_COL_COMPANY":        {"tr": "Şirket",                         "de": "Unternehmen",                         "en": "Company"},
    "CON_COL_POSITION":       {"tr": "Pozisyon",                       "de": "Position",                            "en": "Position"},
    "CON_COL_NAME":           {"tr": "Kişi",                           "de": "Person",                              "en": "Person"},
    "CON_COL_ROLE":           {"tr": "Görev",                          "de": "Rolle",                               "en": "Role"},
    "CON_COL_EMAIL":          {"tr": "E-posta",                        "de": "E-Mail",                              "en": "Email"},
    "CON_COL_PHONE":          {"tr": "Telefon",                        "de": "Telefon",                             "en": "Phone"},
    "CON_COL_MAIL":           {"tr": "Mail",                           "de": "Mail",                                "en": "Mail"},
    "CON_COL_ACTION":         {"tr": "İşlem",                          "de": "Aktion",                              "en": "Action"},
    "CON_TMPL_HEADER":        {"tr": "✏️  E-posta Şablonu",            "de": "✏️  E-Mail-Vorlage",                  "en": "✏️  Email Template"},
    "CON_TMPL_VARS":          {"tr": "Değişkenler:  {kontakt_adi}  {firma_adi}  {pozisyon}  {vorname}  {nachname}",
                               "de": "Variablen:  {kontakt_adi}  {firma_adi}  {pozisyon}  {vorname}  {nachname}",
                               "en": "Variables:  {kontakt_adi}  {firma_adi}  {pozisyon}  {vorname}  {nachname}"},
    "CON_TMPL_SUBJECT":       {"tr": "Konu:",                          "de": "Betreff:",                            "en": "Subject:"},
    "CON_TMPL_BODY":          {"tr": "Metin:",                         "de": "Text:",                               "en": "Body:"},
    "CON_SEND_BTN":           {"tr": "Gönder",                         "de": "Senden",                              "en": "Send"},
    "CON_SENT":               {"tr": "✓ Gönderildi",                   "de": "✓ Gesendet",                          "en": "✓ Sent"},
    "CON_NOT_SENT":           {"tr": "—",                              "de": "—",                                   "en": "—"},
    "CON_PROGRESS":           {"tr": "{n} kontakt  ·  {s} gönderildi", "de": "{n} Kontakte  ·  {s} gesendet",       "en": "{n} contacts  ·  {s} sent"},
    "CON_NO_SMTP":            {"tr": "⚠  SMTP ayarları eksik — Ayarlar sekmesini doldurun!",
                               "de": "⚠  SMTP-Einstellungen fehlen — Bitte Einstellungen ausfüllen!",
                               "en": "⚠  SMTP settings missing — Please fill in Settings!"},
    "CON_NO_CONTACTS":        {"tr": "Gönderilecek kontakt bulunamadı.", "de": "Keine Kontakte zum Senden gefunden.", "en": "No contacts to send to."},
    "CON_ALL_SENT":           {"tr": "Tüm kontaktlara zaten gönderilmiş.", "de": "An alle Kontakte wurde bereits gesendet.", "en": "Already sent to all contacts."},
    "CON_SENDING":            {"tr": "Gönderiliyor {i}/{n}: {addr}",   "de": "Wird gesendet {i}/{n}: {addr}",       "en": "Sending {i}/{n}: {addr}"},
    "CON_SENT_OK":            {"tr": "✓ Gönderildi {i}/{n}: {addr}",  "de": "✓ Gesendet {i}/{n}: {addr}",          "en": "✓ Sent {i}/{n}: {addr}"},
    "CON_ERR":                {"tr": "✗ HATA ({addr}): {err}",         "de": "✗ FEHLER ({addr}): {err}",            "en": "✗ ERROR ({addr}): {err}"},
    "CON_WAIT":               {"tr": "✓ Gönderildi {i}/{n} · Sonraki: {r}s bekleniyor...",
                               "de": "✓ Gesendet {i}/{n} · Nächste in {r}s...",
                               "en": "✓ Sent {i}/{n} · Next in {r}s..."},
    "CON_DONE":               {"tr": "✅ Gönderim tamamlandı — {n} kontakt işlendi.",
                               "de": "✅ Versand abgeschlossen — {n} Kontakte verarbeitet.",
                               "en": "✅ Sending complete — {n} contacts processed."},
}


def set_lang(lang: str) -> None:
    global _current
    if lang in _T.get("APP_TITLE", {}):
        _current = lang


def get_lang() -> str:
    return _current


def t(key: str, **kwargs) -> str:
    """
    Aktif dilde çeviriyi döndürür.
    Bilinmeyen anahtar → anahtarın kendisini döndürür.
    kwargs ile f-string benzeri yerleştirme yapılabilir:
        t("CON_SENDING", i=1, n=5, addr="test@x.de")
    """
    row = _T.get(key)
    if row is None:
        return key
    text = row.get(_current) or row.get("tr") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def init_from_config() -> None:
    """Config dosyasından dil tercihini yükle."""
    try:
        from utils.config import load_config
        lang = load_config().get("lang", "tr")
        set_lang(lang)
    except Exception:
        pass
