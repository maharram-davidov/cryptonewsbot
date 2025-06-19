# 🤖 Kripto Xəbər Botu (Crypto News Bot)

Real-time kripto xəbərlərini AI analizi ilə birlikdə paylaşan Telegram bot.

## 🎯 Əsas Funksiyalar

- **📰 Real-time xəbər paylaşımı**: CoinDesk, The Block, Cointelegraph kimi mənbələrdən
- **🧠 AI analizi**: Hər xəbər üçün Google Gemini 2.0 Flash ilə market təsiri və risk analizi
- **🕐 Azərbaycan saatı**: Xəbərlərdə tarix və saat AZT (Asia/Baku) zona saatı ilə göstərilir
- **📊 Sinxron arxitektura**: Stabil və sürətli işləmə üçün sinxron kod strukturu
- **⚡ Avtomatik yenilənmə**: 5 dəqiqədə bir yeni xəbər yoxlanması
- **👥 Abunəlik sistemi**: İstifadəçilər abunə olub xəbər ala bilərlər

## 🛠️ Texniki Xüsusiyyətlər

- **Python-telegram-bot v13.15**: Stabil sinxron handler dəstəyi
- **Sinxron kod**: Bütün funksiyalar sinxron, async/await yoxdur
- **Windows uyğunluğu**: Event loop problemləri həll edilib
- **RSS əsaslı**: API limitləri olmadan xəbər çəkilməsi

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

### Botu başlatmaq:
```bash
python main.py
```

### Test etmək:
```bash
python test_bot.py
```

## 📋 Bot Komandaları

- `/start` - Botu başlat və tanıtım
- `/subscribe` - Xəbər abunəliyini aktivləşdir
- `/unsubscribe` - Abunəliyi dayandır  
- `/latest` - Son 3 xəbəri göstər
- `/status` - Bot statusu və statistika
- `/help` - Kömək məlumatı
- `/admin` - Admin paneli (yalnız adminlər üçün)

## 🏗️ Layihə Strukturu

```
CryptoNewsBot/
├── main.py              # Ana fayl - botu işə salır (sinxron)
├── bot.py               # Telegram bot funksiyaları (PTB v13.15)
├── config.py            # Konfiqurasiya və parametrlər
├── news_fetcher.py      # Xəbər çəkmə sinifləri (sinxron)
├── ai_analyzer.py       # AI analiz funksiyaları (sinxron)
├── test_bot.py          # Test skripti
├── requirements.txt     # Python paketləri (PTB v13.15)
├── env_example.txt      # Environment nümunəsi
└── README.md           # Bu fayl
```

## ⚙️ Konfiqurasiya

`config.py` faylında aşağıdakı parametrləri dəyişə bilərsiniz:

```python
BOT_SETTINGS = {
    'check_interval': 300,      # Yoxlama intervalı (saniyə) - 5 dəqiqə
    'max_news_per_check': 5,    # Hər yoxlamada max xəbər sayı
    'ai_analysis': True,        # AI analizi aktiv/deaktiv
    'send_to_channels': True    # Kanallara göndərmə
}

AI_SETTINGS = {
    'model': 'gemini-2.0-flash',    # AI model
    'max_tokens': 200,              # Maksimum token sayı
    'temperature': 0.7,             # Yaradıcılıq səviyyəsi
}
```

## 📊 Xəbər Mənbələri

1. **CoinDesk**: RSS feed (`https://www.coindesk.com/arc/outboundfeeds/rss/`)
2. **The Block**: RSS feed (`https://www.theblock.co/rss.xml`)
3. **Cointelegraph**: RSS feed (`https://cointelegraph.com/rss`)
4. **Crypto News**: RSS feed (`https://crypto.news/feed/`)
5. **NewsBTC**: RSS feed (`https://www.newsbtc.com/feed/`)

**Qeyd**: Bütün mənbələr RSS vasitəsi ilə çəkilir, API key tələb etmir.

## 🧠 AI Analizi

Hər xəbər üçün Google Gemini 2.0 Flash modeli ilə analiz:

- **🔥 Market Təsiri**: Bullish/Bearish/Neytral
- **📊 Risk Səviyyəsi**: Aşağı/Orta/Yüksək  
- **💡 Qısa Analiz**: 1-2 cümlə ilə xəbərin qiymətləndirilməsi
- **🇦🇿 Azərbaycan dilində**: Bütün analizlər Azərbaycan dilində

Əgər Gemini API əlçatmaz olarsa, fallback analiz sistemi açar sözlərə əsasən işləyir.

## 🕐 Zaman Zona Dəstəyi

- Bütün xəbər tarixləri **Azərbaycan saatı (AZT)** ilə göstərilir
- UTC-dən avtomatik çevrilmə: `Asia/Baku` timezone
- Format: `DD.MM.YYYY HH:MM (AZT)`

## 📦 Paket Versiyaları

```
python-telegram-bot==13.15  # Stabil sinxron dəstək
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

## 🚨 Problemlər və Həllər

### Bot başlamır:
- Virtual environment-in aktivləşdirildiyini yoxlayın
- `pip install -r requirements.txt` ilə paketləri yenidən yükləyin
- `.env` faylının mövcud olduğunu təsdiq edin

### Xəbər çəkilmir:
- İnternet bağlantısını yoxlayın
- RSS URL-lərinin aktiv olduğunu təsdiq edin
- `test_bot.py` ilə komponentləri test edin

### AI analizi işləmir:
- Gemini API key-inin düzgün olduğunu yoxlayın
- API limitlərini yoxlayın
- Fallback analiz sistemi avtomatik işləyəcək

### Telegram mesajları getmir:
- Bot token-ının düzgün olduğunu yoxlayın
- Botun istifadəçi tərəfindən bloklanmadığını yoxlayın

### Event loop xətaları (Windows):
- PTB v13.15 istifadə edildiyindən bu problem həll edilib
- Sinxron kod strukturu event loop problemlərini aradan qaldırır

## 🆕 Son Yeniliklər

- ✅ **PTB v13.15**: Event loop problemləri həll edildi
- ✅ **Sinxron struktur**: Async/await yoxdur, daha stabil
- ✅ **Azərbaycan saatı**: AZT timezone dəstəyi
- ✅ **Gemini 2.0 Flash**: Yeni AI model dəstəyi
- ✅ **Windows uyğunluğu**: IDE və terminal problemləri həll edildi
- ✅ **RSS fokus**: API limitləri olmadan xəbər çəkilməsi

## 📞 Dəstək

Problemlər üçün:
- GitHub Issues bölməsində issue açın
- Telegram: @your_username

## 📄 Lisenziya

MIT License - ətraflı məlumat üçün LICENSE faylına baxın.

---

⭐ Layihə faydalı olubsa, GitHub-da ulduz verməyi unutmayın! 