import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Google Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# News Sources Configuration
NEWS_SOURCES = {
    'coindesk': {
        'rss_url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'api_url': 'https://www.coindesk.com/api/v1/news',
        'name': 'CoinDesk'
    },
    'theblock': {
        'rss_url': 'https://www.theblock.co/rss.xml',
        'name': 'The Block'
    },
    'cointelegraph': {
        'rss_url': 'https://cointelegraph.com/rss',
        'name': 'Cointelegraph'
    }
}

# Bot Settings
BOT_SETTINGS = {
    'check_interval': 300,  # 5 minutes
    'max_news_per_check': 5,
    'ai_analysis': True,
    'send_to_channels': True
}

# AI Analysis Settings
AI_SETTINGS = {
    'model': 'gemini-2.0-flash',
    'max_tokens': 200,
    'temperature': 0.7,
    'analysis_prompt': """
Aşağıdakı kripto xəbəri analiz edin və qısa bir yorum yazın:

Xəbər: {news_content}

Yorumunuzda aşağıdakıları daxil edin:
- Market təsiri (Bullish/Bearish/Neytral)
- Qısa analiz (1-2 cümlə)
- Risk səviyyəsi (Aşağı/Orta/Yüksək)

Format:
🔥 Market Təsiri: [Bullish/Bearish/Neytral]
📊 Analiz: [Qısa analiz]
⚠️ Risk: [Aşağı/Orta/Yüksək]
"""
}

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'crypto_bot.log' 