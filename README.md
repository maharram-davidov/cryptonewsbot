# 🤖 Kripto Xəbər Botu (Crypto News Bot)

Real-time kripto xəbərlərini AI analizi və günlük özet ilə birlikdə paylaşan akıllı Telegram bot.

## 🎯 Əsas Funksiyalar

- **📰 Real-time xəbər paylaşımı**: CoinDesk, The Block, Crypto News, NewsBTC kimi mənbələrdən
- **🧠 AI analizi**: Hər xəbər üçün Google Gemini 2.0 Flash ilə market təsiri və risk analizi
- **🌙 Günlük AI özet**: Hər gecə 00:05'tə günün ən vacib xəbərlərinin AI analizi
- **⚙️ Kullanıcı ayarları**: Anlık bildirimləri və günlük özeti ayrı ayrı açıp bağlama
- **💾 Kalıcı veri saklama**: Abunəlik və ayar bilgiləri JSON fayllarında saxlanır
- **🕐 Azərbaycan saatı**: Xəbərlərdə tarix və saat AZT (Asia/Baku) zona saatı ilə göstərilir
- **📊 Sinxron arxitektura**: Stabil və sürətli işləmə üçün sinxron kod strukturu
- **⚡ Avtomatik yenilənmə**: 90 saniyədə bir yeni xəbər yoxlanması
- **👥 İntellektual abunəlik sistemi**: İstifadəçilər bildirim tercihləri edə bilərlər


## ✨ Yeni Özellikler

### 🎛️ Kullanıcı Bildirim Ayarları
- **🔔 Anlık Xəbərlər**: Real-time kripto xəbərlərini açıp bağlaya bilərsiniz
- **📅 Günlük Özet**: Gece sabit saatdəki AI özetini açıp bağlaya bilərsiniz  
- **⚙️ Kolay Yönetim**: `/settings` komutu ilə buton tabanlı kontrol
- **🎯 Kişiselleştirme**: Hər istifadəçi öz tercihini yarada bilər

### 🌙 Günlük AI Özet Sistemi
- **🕐 Otomatik Zamanlama**: Hər gecə 00:05'tə otomatik özet
- **🤖 AI Analizi**: Son 24 saatın ən önemli xəbərlərinin Gemini analizi
- **📊 Market Durumu**: Günlük trend analizi (Bullish/Bearish/Neytral)
- **📋 Özet Format**: Önemli xəbərlər, bazar analizi və risk seviyyəsi
- **🔧 Manuel Kontrolü**: Adminlər istədikləri vaxt `/daily_summary` ilə gönderə bilərlər

### 💾 Kalıcı Veri Saklama Sistemi
- **👥 Abunəlik Verisi**: `subscribers.json` dosyasında kalıcı saklama
- **⚙️ Kullanıcı Ayarları**: `user_settings.json` dosyasında tercihlər
- **🔄 Bot Yeniden Başlatma**: Veriler kaybolmadan sistem devam eder
- **🛡️ Güvenlik**: Hassas dosyalar `.gitignore` içinde korunur



## 🛠️ Texniki Xüsusiyyətlər

- **Python-telegram-bot v20.x**: Modern async handler dəstəyi
- **Dual Bot System**: Həm async (`telegram_bot.py`) həm sync (`bot.py`) versiyalar
- **Windows/Linux uyğunluğu**: Bütün platformlarda stabil çalışma
- **RSS əsaslı**: API limitləri olmadan xəbər çəkilməsi
- **JSON Data Persistence**: Kullanıcı verilerinin kalıcı saklanması

## 🚀 Quraşdırma

### 1. Layihəni klonlayın
```bash
git clone https://github.com/your-username/crypto-news-bot.git
cd crypto-news-bot
```

### 2. Virtual environment yaradın
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Tələb olunan paketləri yükləyin
```bash
pip install -r requirements.txt
```

### 4. Environment dəyişənlərini təyin edin

`env_example.txt` faylını `.env` adı ilə kopyalayın və doldurün:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Google Gemini Configuration  
GEMINI_API_KEY=your_gemini_api_key_here



# Admin User IDs (comma separated)
ADMIN_USER_IDS=123456789,987654321
```

### 5. API Key-lərini əldə edin

#### Telegram Bot Token:
1. [@BotFather](https://t.me/botfather) ilə əlaqə saxlayın
2. `/newbot` komandası ilə yeni bot yaradın
3. Bot token-ını kopyalayın

#### Google Gemini API Key:
1. [Google AI Studio](https://makersuite.google.com/app/apikey) saytına daxil olun
2. Google hesabınızla giriş edin
3. "Create API Key" düyməsini basın

## 🎮 İstifadə

### Modern Bot (Async) - Tövsiyə olunan:
```bash
python main.py  # telegram_bot.py istifadə edir
```

### Legacy Bot (Sync) - Köhnə versiyalar üçün:
```bash
# main.py'de bot.py import edin
python main.py
```

### Test etmək:
```bash
python test_bot.py
```



## 📋 Bot Komandaları

### 👤 İstifadəçi Komandaları
- `/start` - Botu başlat və tanıtım menüsü
- `/subscribe` - Xəbər abunəliyini aktivləşdir
- `/unsubscribe` - Abunəliyi dayandır  
- `/settings` - **YENİ!** Bildirim ayarlarını idarə et
- `/latest` - Son 3 xəbəri göstər
- `/status` - Bot statusu və statistika
- `/help` - Kömək məlumatı

### 🔧 Admin Komandaları
- `/admin` - Admin paneli və statistikalar
- `/daily_summary` - **YENİ!** Manuel günlük özet göndər
- `/reset_news` - Görülən xəbər cache'ini temizlə

### 🎛️ İnline Butonlar
- **📰 Abunə ol** - Tez abunəlik
- **📊 Son xəbərlər** - Son xəbərləri göstər
- **⚙️ Ayarlar** - Bildirim ayarları menüsü
- **ℹ️ Kömək** - Yardım məlumatları

## 🎯 Kullanıcı Ayarları Sistemi

### ⚙️ Ayarlar Menüsü (`/settings`)
```
⚙️ BİLDİRİM AYARLARI

👤 İstifadəçi: Ali
📊 Abunəlik statusu: Aktiv

🔔 Anlık Xəbərlər: 🔔 AÇIQ
   • Real-time kripto xəbərləri
   • Gün ərzində gələn yeniliklər

📅 Günlük Özet: 📅 AÇIQ  
   • Hər gecə saat 00:05'tə
   • AI ilə hazırlanan günün özeti

💡 İpucu: Anlık xəbərləri bağlasanız da günlük özet almağa davam edə bilərsiniz!
```

### 🎮 Kullanım Senaryaları
1. **📱 Sadece Anlık Haberler**: Anlık açık, günlük kapalı
2. **🌙 Sadece Günlük Özet**: Anlık kapalı, günlük açık  
3. **📺 Tam Bilgilendirme**: İkisi də açık
4. **🔕 Geçici Susturma**: İkisi də kapalı

## 🏗️ Layihə Strukturu

```
CryptoNewsBot/
├── main.py                   # Ana fayl - botu işə salır
├── telegram_bot.py           # Modern async bot (PTB v20.x) 
├── bot.py                    # Legacy sync bot (PTB v13.15)
├── config.py                 # Konfiqurasiya və parametrlər
├── news_fetcher.py           # Xəbər çəkmə sinifləri
├── ai_analyzer.py            # AI analiz funksiyaları

├── test_bot.py               # Test skripti
├── requirements.txt          # Python paketləri
├── env_example.txt           # Environment nümunəsi
├── railway.toml              # Deploy konfigürasyonu
├── runtime.txt               # Python versiyası
├── subscribers.json          # 💾 Abunə verisi (auto-generated)
├── user_settings.json        # 💾 Kullanıcı ayarları (auto-generated)
├── seen_news.json            # 💾 Görülən xəbər cache (auto-generated)

└── README.md                # Bu fayl
```

## ⚙️ Konfiqurasiya

`config.py` faylında aşağıdakı parametrləri dəyişə bilərsiniz:

```python
BOT_SETTINGS = {
    'check_interval': 90,       # Yoxlama intervalı (saniyə) - 1.5 dəqiqə
    'max_news_per_check': 5,    # Hər yoxlamada max xəbər sayı
    'ai_analysis': True,        # AI analizi aktiv/deaktiv
    'send_to_channels': True    # Kanallara göndərmə
}

AI_SETTINGS = {
    'model': 'gemini-2.0-flash',    # AI model
    'max_tokens': 200,              # Maksimum token sayı
    'temperature': 0.7,             # Yaradıcılıq səviyyəsi
    'analysis_prompt': "..."        # AI analiz prompt-u
}
```

## 📊 Xəbər Mənbələri

1. **CoinDesk**: RSS feed (`https://www.coindesk.com/arc/outboundfeeds/rss/`)
2. **The Block**: RSS feed (`https://www.theblock.co/rss.xml`)
3. **Crypto News**: RSS feed (`https://crypto.news/feed/`)
4. **NewsBTC**: RSS feed (`https://www.newsbtc.com/feed/`)

**Qeyd**: Bütün mənbələr RSS vasitəsi ilə çəkilir, API key tələb etmir.

## 🧠 AI Analizi

### 📰 Anlık Xəbər Analizi
Hər xəbər üçün Google Gemini 2.0 Flash modeli ilə:
- **🔥 Market Təsiri**: Bullish/Bearish/Neytral
- **📊 Risk Səviyyəsi**: Aşağı/Orta/Yüksək  
- **💡 Qısa Analiz**: 1-2 cümlə ilə xəbərin qiymətləndirilməsi
- **🇦🇿 Azərbaycan dilində**: Bütün analizlər Azərbaycan dilində

### 🌙 Günlük Özet Analizi
```
🌙 GÜNLÜK XƏBƏRLƏRİN ÖZETİ
📅 Tarix: 15.12.2024
📊 Ümumi Bazar Durumu: Bullish

🔥 ÖNƏMLİ XƏBƏRLƏR:
• Bitcoin 42000$ səviyyəsini keçdi
• Ethereum'da yeni protokol güncellemesi
• BlackRock-un Bitcoin ETF başvurusu

📈 BAZAR ANALİZİ:
• Market trend-i: Yükselen
• Risk seviyyesi: Orta
• Yatırım tavsiyesi: Dikkatli iyimser

🎯 QISA NƏTICƏ:
Son 24 saatda pozitif gelişmeler gözlemlendi.
```

## 🕐 Zaman Zona Dəstəyi

- Bütün xəbər tarixləri **Azərbaycan saatı (AZT)** ilə göstərilir
- UTC-dən avtomatik çevrilmə: `Asia/Baku` timezone
- Format: `DD.MM.YYYY HH:MM (AZT)`
- Günlük özet: Hər gecə **00:05 AZT**

## 💾 Veri Saklama Sistemi

### 📁 Otomatik Oluşan Dosyalar
- **`subscribers.json`**: Abunə olmuş kullanıcıların listəsi
- **`user_settings.json`**: Hər kullanıcının bildirim tercihleri
- **`seen_news.json`**: Görülən xəbər cache'i (dublikat önleme)

### 🛡️ Güvenlik
Tüm kullanıcı verisi dosyaları `.gitignore` içində korunur ve git'e commit edilmez.

### 🔄 Veri Formatları
```json
// subscribers.json
{
  "subscribers": [123456789, 987654321],
  "last_updated": "2024-12-15T10:30:00",
  "total_count": 2
}

// user_settings.json  
{
  "123456789": {
    "instant_notifications": true,
    "daily_summary": true,
    "joined_date": "2024-12-15T10:30:00",
    "last_activity": "2024-12-15T10:30:00"
  }
}
```

## 📦 Paket Versiyaları

```
# Modern Version (telegram_bot.py)
python-telegram-bot>=20.0   # Modern async dəstək
asyncio                      # Async işlemler

# Legacy Version (bot.py) 
python-telegram-bot==13.15  # Stabil sinxron dəstək

# Ortak Paketler
requests==2.31.0             # HTTP sorğuları
feedparser==6.0.10           # RSS parser
google-generativeai==0.3.2   # Gemini AI
beautifulsoup4==4.12.2       # HTML parser
python-dotenv==1.0.0         # Environment dəyişənləri
APScheduler==3.6.3           # Job scheduler
pytz==2023.3                 # Timezone dəstəyi
```

## 📝 Log və Monitoring

- Bütün fəaliyyətlər `crypto_bot.log` faylında qeyd olunur
- Real-time konsol çıxışı mövcuddur
- Xəta hallarında avtomatik recovery
- Job queue ilə avtomatik xəbər yoxlanması
- Kullanıcı ayar değişikliklərinin loglanması
- Günlük özet gönderim istatistikləri

## 🔧 Təkmilləşdirmə

### Yeni xəbər mənbəyi əlavə etmək:

1. `config.py`-də `NEWS_SOURCES`-ə əlavə edin:
```python
'new_source': {
    'rss_url': 'https://example.com/rss.xml',
    'name': 'New Source'
}
```

2. `news_fetcher.py`-də yeni fetch funksiyası yazın
3. `fetch_all_news()` metoduna daxil edin

### AI analiz modelini dəyişmək:

`config.py`-də `AI_SETTINGS` bölməsində model parametrlərini dəyişin:
```python
AI_SETTINGS = {
    'model': 'gemini-pro',  # və ya başqa model
    'max_tokens': 300,
    'temperature': 0.5
}
```

### Günlük özet saatini dəyişmək:

`telegram_bot.py` və ya `bot.py`-də job queue konfigurasiyasını dəyişin:
```python
job_queue.run_daily(
    self.daily_summary_job,
    time=datetime.now().time().replace(hour=1, minute=0)  # 01:00'da
)
```

## 🚨 Problemlər və Həllər

### Bot başlamır:
- Virtual environment-in aktivləşdirildiyini yoxlayın
- `pip install -r requirements.txt` ilə paketləri yenidən yükləyin
- `.env` faylının mövcud olduğunu təsdiq edin

### Abunəlik verisi kaybolur:
- ✅ **Həll edildi!** Artık `subscribers.json` faylında kalıcı saklama
- Bot yeniden başladıldığında veriler otomatik yüklənir

### Xəbər çəkilmir:
- İnternet bağlantısını yoxlayın
- RSS URL-lərinin aktiv olduğunu təsdiq edin
- `test_bot.py` ilə komponentləri test edin

### AI analizi işləmir:
- Gemini API key-inin düzgün olduğunu yoxlayın
- API limitlərini yoxlayın
- Fallback analiz sistemi avtomatik işləyəcək

### Günlük özet gəlmir:
- Kullanıcı ayarlarında günlük özet açık olduğunu yoxlayın (`/settings`)
- Bot timezone ayarlarını yoxlayın (AZT - Asia/Baku)
- Manuel test üçün `/daily_summary` admin komandası istifadə edin

### Bildirimlər gəlmir:
- `/settings` komandası ilə bildirimlerin açık olduğunu yoxlayın
- Bot token-ının düzgün olduğunu yoxlayın
- Botun istifadəçi tərəfindən bloklanmadığını yoxlayın

## 🆕 Son Yeniliklər (v2.0)

- ✅ **Kullanıcı Ayarları Sistemi**: Bildirimləri ayrı ayrı kontrol
- ✅ **Günlük AI Özet**: Hər gecə otomatik özet gönderimi  
- ✅ **Kalıcı Veri Saklama**: JSON dosyalarında kullanıcı verilerinin korunması
- ✅ **Dual Bot System**: Həm async həm sync versiyalar
- ✅ **İntelligent Broadcasting**: Kullanıcı tercihlərinə görə gönderim
- ✅ **Modern UI**: İnline butonlar ilə kolay yönetim
- ✅ **Admin Panel Geliştirmeleri**: Manual özet və detaylı istatistikler
- ✅ **PTB v20.x Dəstəyi**: Modern async handler yapısı
- ✅ **Azərbaycan saatı**: AZT timezone dəstəyi
- ✅ **Gemini 2.0 Flash**: Yeni AI model dəstəyi
- ✅ **Windows/Linux uyğunluğu**: Cross-platform stabil çalışma

## 📊 Sistem Özellikleri

### 🎯 Performans
- **⚡ Hızlı Yanıt**: İnline butonlarla anında ayar değişimi
- **📊 Akıllı Cache**: Görülən xəbərlərin optimize edilmiş saklanması
- **🔄 Rate Limiting**: Telegram API limitlərinə uygun gönderim
- **💾 Memory Optimization**: Veri saklama için optimize edilmiş JSON struktur

### 🛡️ Güvenlik
- **🔐 Admin Kontrolü**: Hassas komandlar için admin doğrulaması
- **🚫 Data Protection**: Hassas dosyalar git'e commit edilmez
- **🔍 Input Validation**: Kullanıcı girişlərinin doğrulanması
- **📝 Audit Logging**: Tüm önemli işlemlerin loglanması

## 📞 Dəstək

Problemlər üçün:
- GitHub Issues bölməsində issue açın
- Telegram: @davudov07
- Email: destek@cryptobot.az