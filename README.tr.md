<div align="center">

**🌐 Language / Sprache / Dil:**
[🇬🇧 English](README.md) &nbsp;|&nbsp; [🇹🇷 Türkçe](README.tr.md) &nbsp;|&nbsp; [🇩🇪 Deutsch](README.de.md)

# 🎓 AusbildungBot

**Ausbildung.de için otomatik staj başvurusu botu**

[![Release](https://img.shields.io/github/v/release/ck-cankurt/ausbildungbot?style=for-the-badge&color=5b2d8e)](https://github.com/ck-cankurt/ausbildungbot/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078d4?style=for-the-badge&logo=windows)](https://github.com/ck-cankurt/ausbildungbot/releases)
[![Powered by Ubden](https://img.shields.io/badge/Powered%20by-Ubden%20Open%20Source%20Community-9060c0?style=for-the-badge)](https://github.com/ubden)

<br/>

> Almanya'daki Ausbildung ilanlarına ausbildung.de üzerinden otomatik başvuru yapan yapay zeka destekli masaüstü uygulaması.  
> Playwright ile gerçek tarayıcı kontrolü · OpenAI GPT-4o-mini ile kişisel Anschreiben üretimi · 3 dil desteği (TR / DE / EN)

<br/>

</div>

---

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🤖 **Otomatik Başvuru** | ausbildung.de'deki direkt başvuru ilanlarını bulur ve formu otomatik doldurur |
| 📝 **AI Anschreiben** | Her ilana özel Almanca *Kurz-Anschreiben* üretir (GPT-4o-mini) |
| 📄 **PDF Üretimi** | Gerektiğinde PDF *Anschreiben* oluşturur ve yükler |
| 🔍 **Akıllı Filtreleme** | Şehir, yarıçap, sektör, eğitim türü ve kelime bazlı filtreleme |
| 📬 **Kontakt Yönetimi** | İlan sayfalarından irtibat kişilerini otomatik toplar |
| 📧 **Toplu Mail** | Toplanan kontaktlara şablonlu mail gönderir (5 saniyelik aralıkla) |
| 📱 **Telegram Bildirimleri** | Başarılı her başvuru için formatlı Telegram mesajı gönderir |
| 📊 **Başvuru Raporu** | Tüm başvuruları durum, şirket ve tarih bazlı listeler |
| 🔒 **Yerel Depolama** | Tüm veriler SQLite'a kaydedilir — hiçbir şey buluta gönderilmez |
| 🌐 **3 Dil Desteği** | Türkçe, Almanca ve İngilizce arayüz; istediğin zaman değiştir |
| 🖥 **Modern Arayüz** | customtkinter ile geliştirilmiş dark mode masaüstü arayüzü |

---

## 📸 Ekran Görüntüleri

<details>
<summary><b>🖼 Ekran görüntülerini görmek için tıklayın</b></summary>

<br/>

**Giriş Sekmesi — Hesap bilgileri + Profil uyarısı**
> *(Buraya `screenshots/login.png` ekleyin)*

**Bot Sekmesi — Başlatma, kelime filtresi, canlı log**
> *(Buraya `screenshots/bot.png` ekleyin)*

**Ayarlar Sekmesi — OpenAI, SMTP, Telegram, filtreler**
> *(Buraya `screenshots/settings.png` ekleyin)*

**Başvurular Sekmesi — Tablo ve istatistikler**
> *(Buraya `screenshots/applications.png` ekleyin)*

**Kontaktlar Sekmesi — İrtibat listesi ve mail gönderme**
> *(Buraya `screenshots/contacts.png` ekleyin)*

</details>

---

## 🚀 Kurulum

### Yöntem 1: Hazır EXE (Önerilen — Windows)

1. [Releases](https://github.com/ck-cankurt/ausbildungbot/releases/latest) sayfasından son sürümü indirin
2. ZIP dosyasını bir klasöre çıkartın
3. `kurulum.bat` dosyasını **yönetici olarak** çalıştırın — Chromium tarayıcısını indirir (~150 MB)
4. `AusbildungBot.exe` dosyasını çalıştırın

```
AusbildungBot/
├── AusbildungBot.exe     ← Çalıştırılacak uygulama
├── kurulum.bat           ← İLK KULLANIM: Chromium'u indirir
├── playwright_browsers/  ← kurulum.bat sonrası otomatik oluşur
├── config.json           ← Ayarlar (otomatik oluşturulur)
└── applications.db       ← Başvuru veritabanı (otomatik oluşturulur)
```

---

### Yöntem 2: Kaynak Koddan Çalıştırma

**Gereksinimler:** Python 3.11+, pip

```bash
# 1. Repoyu klonla
git clone https://github.com/ck-cankurt/ausbildungbot.git
cd ausbildungbot

# 2. Bağımlılıkları kur
pip install -r requirements.txt

# 3. Playwright tarayıcısını kur
playwright install chromium

# 4. Uygulamayı başlat
python main.py
```

---

## ⚙️ Yapılandırma

Uygulama ilk çalıştırmada `config.json` dosyasını otomatik oluşturur. Tüm ayarlar arayüzden yapılır:

### Giriş Sekmesi
- ausbildung.de e-posta ve şifre

### Ayarlar Sekmesi

| Alan | Açıklama |
|------|----------|
| OpenAI API Key | `sk-…` formatında GPT-4o-mini için gerekli |
| Şehir | Arama yapılacak şehir (ör: Heidelberg) |
| Yarıçap | 10 / 25 / 50 / 100 / 200 km |
| Branche | 25 sektör seçeneği |
| Kişisel Bilgiler | Vorname, Nachname, Adres (PDF için) |
| SMTP Ayarları | Mail göndermek için SMTP sunucu bilgileri |
| Telegram Bildirimleri | Başvuru bildirimleri için bot token + Chat ID |

### Bot Sekmesi — Kelime Filtresi

```
🔍 Kelime Filtresi: [ kalt          ]
                    [ Kaufmann       ]
                    [ Informatik     ]
                    [ boş = tümü    ]
```

Kelime girildiğinde arama URL'si şu şekilde oluşur:
```
https://www.ausbildung.de/suche/?search=kalt|Mannheim&radius=50
```

---

## 🤖 Bot Nasıl Çalışır?

```
Bot Başlat
  └─ Tarayıcı açılır (Chromium)
  └─ ausbildung.de'ye giriş yapılır
  └─ İlanlar taranır (scroll + "Mehr Ergebnisse laden")
       └─ Her direkt başvuru ilanı için:
            ├─ DB'de zaten var mı? → atla
            ├─ İrtibat kişisi kaydedilir (varsa)
            ├─ "Bereits beworben" → already_applied
            ├─ Form doldurulur (5 adım):
            │    ├─ Adım 1: Kişisel veriler
            │    ├─ Adım 2: İletişim bilgileri
            │    ├─ Adım 3: Zeugnisse (profilden)
            │    ├─ Adım 4: Anschreiben (AI üretimi + PDF upload)
            │    └─ Adım 5: Dosyalar (profilden)
            ├─ Überprüfen → Bewerbung abschicken
            ├─ Doğrulama: ilan sayfasına geri dön
            └─ DB'ye kaydet → GUI + Telegram bildirimi (açıksa)
  └─ Tamamlandı: Başvurulan / Atlanan / Hata raporu
```

---

## 📧 SMTP Mail Ayarları (Gmail örneği)

1. Gmail hesabınızda **2 adımlı doğrulama** etkinleştirin
2. [App Passwords](https://myaccount.google.com/apppasswords) sayfasından uygulama şifresi oluşturun
3. Ayarlar sekmesine girin:

```
SMTP Sunucu:  smtp.gmail.com
SMTP Port:    587
E-posta:      ornek@gmail.com
Şifre:        xxxx xxxx xxxx xxxx  (uygulama şifresi)
STARTTLS:     ✅ açık
```

---

## 📱 Telegram Bildirimleri

Telegram bildirimleri isteğe bağlıdır ve Ayarlar sekmesinden açılır. Açıldığında bot, başarıyla tamamlanan her `applied` başvurudan sonra formatlı bir Telegram mesajı gönderir.

1. Telegram'da [@BotFather](https://t.me/BotFather) hesabını açın ve `/newbot` ile bot oluşturun
2. Verilen API token değerini **Bot API Token** alanına yapıştırın
3. Oluşturduğunuz bota herhangi bir mesaj gönderin
4. [@userinfobot](https://t.me/userinfobot) hesabına `/start` yazın ve gelen `Id` değerini **Chat ID** alanına girin
5. Ayarlar sekmesindeki **Test Mesajı Gönder** butonuyla bağlantıyı doğrulayın

---

## 🔨 EXE Build (Kaynak Koddan)

```bash
pip install pyinstaller
pyinstaller ausbildung.spec --clean -y
```

Çıktı: `dist/AusbildungBot/AusbildungBot.exe`

---

## 📁 Proje Yapısı

```
ausbildungbot/
├── main.py                    # Giriş noktası
├── requirements.txt           # Python bağımlılıkları
├── ausbildung.spec            # PyInstaller konfigürasyonu
├── kurulum.bat                # Chromium kurulum betiği
│
├── gui/                       # Kullanıcı arayüzü (customtkinter)
│   ├── app.py                 # Ana pencere + sekme yöneticisi
│   ├── login_tab.py           # Giriş + önemli not
│   ├── settings_tab.py        # Ayarlar (OpenAI, filtreler, SMTP, Telegram)
│   ├── bot_tab.py             # Bot kontrolü + kelime filtresi + log
│   ├── applications_tab.py    # Başvuru tablosu + istatistikler
│   └── contacts_tab.py        # Kontaktlar + toplu mail
│
├── bot/                       # Bot motoru
│   ├── browser.py             # Playwright başlatma/kapatma
│   ├── login.py               # ausbildung.de giriş akışı
│   ├── scraper.py             # İlan tarama + URL oluşturma
│   ├── applicator.py          # Form doldurma + başvuru
│   └── runner.py              # Bot iş akışı yöneticisi
│
├── services/                  # Harici servisler
│   ├── database.py            # SQLite CRUD (applications + contacts)
│   ├── openai_service.py      # GPT-4o-mini Anschreiben üretimi
│   ├── pdf_service.py         # ReportLab PDF üretimi
│   ├── smtp_service.py        # SMTP mail gönderme
│   └── telegram_service.py    # Telegram Bot API bildirimleri
│
└── utils/
    ├── config.py              # config.json okuma/yazma
    └── i18n.py                # Çeviriler (TR / DE / EN)
```

---

## ⚠️ Önemli Notlar

- **Profil eksiksiz olmalı:** Botu başlatmadan önce ausbildung.de profilinizin tam dolu olduğundan emin olun. CV, fotoğraf ve belgeler yüklü olmalıdır.
- **OpenAI API Key:** GPT-4o-mini ile Anschreiben üretimi için gereklidir. Olmadan bot Anschreiben alanını boş bırakır.
- **Yasal sorumluluk:** Bu bot, kullanıcının kendi hesabıyla kendi adına başvuru yapması için tasarlanmıştır. Başvuruların kalitesinden ve içeriğinden kullanıcı sorumludur.
- **Oran sınırı:** ausbildung.de'nin bot koruması olabilir. Çok hızlı başvuru yapılırsa geçici engelleme oluşabilir.

---

## 🛠 Bağımlılıklar

| Paket | Versiyon | Kullanım |
|-------|----------|----------|
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | ≥5.2.2 | Modern GUI çerçevesi |
| [playwright](https://playwright.dev/python/) | ≥1.44.0 | Tarayıcı otomasyonu |
| [openai](https://github.com/openai/openai-python) | ≥1.30.0 | AI Anschreiben üretimi |
| [reportlab](https://www.reportlab.com/) | ≥4.0.0 | PDF oluşturma |
| [Pillow](https://python-pillow.org/) | ≥10.0.0 | Görsel işleme (ReportLab bağımlılığı) |

---

## 🤝 Katkı

Pull request'ler ve issue'lar memnuniyetle karşılanır!

1. Repoyu fork yapın
2. Feature branch oluşturun: `git checkout -b feature/yeni-ozellik`
3. Commit'leyin: `git commit -m 'Yeni özellik: ...'`
4. Push yapın: `git push origin feature/yeni-ozellik`
5. Pull Request açın

---

## 📜 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Serbestçe kullanabilir, değiştirebilir ve dağıtabilirsiniz.

---

<div align="center">

**Powered by [Ubden Open Source Community](https://github.com/ubden)**

[![GitHub](https://img.shields.io/badge/GitHub-ck--cankurt-181717?style=flat-square&logo=github)](https://github.com/ck-cankurt)
[![Bağış](https://img.shields.io/badge/♥-Bağış%20Yap-ff69b4?style=flat-square)](https://ubd.one/donate)

*Bu projeyi faydalı bulduysan bir ⭐ bırakmayı unutma!*

</div>
