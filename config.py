import os
from dotenv import load_dotenv
import logging

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

    'cryptonews': {
        'rss_url': 'https://crypto.news/feed/',
        'name': 'Crypto News'
    },
    'newsbtc': {
        'rss_url': 'https://www.newsbtc.com/feed/',
        'name': 'NewsBTC'
    }
}

# Bot Settings
BOT_SETTINGS = {
    'check_interval': 90,  # 1.5 minutes
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

# Admin Configuration
ADMIN_USER_IDS_STR = os.getenv('ADMIN_USER_IDS', '5387921878')  # Default admin ID
ADMIN_USER_IDS = [int(id.strip()) for id in ADMIN_USER_IDS_STR.split(',') if id.strip()]

# Enhanced Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | Line:%(lineno)-4d | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s | %(levelname)-8s | %(message)s',
            'datefmt': '%H:%M:%S'
        },
        'performance': {
            'format': '%(asctime)s | PERF | %(message)s',
            'datefmt': '%H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file_main': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': 'logs/crypto_bot.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf-8'
        },
        'file_error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/crypto_bot_errors.log',
            'maxBytes': 5242880,  # 5MB
            'backupCount': 3,
            'encoding': 'utf-8'
        },
        'file_performance': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'performance',
            'filename': 'logs/performance.log',
            'maxBytes': 5242880,  # 5MB
            'backupCount': 2,
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file_main', 'file_error'],
            'level': 'INFO',
            'propagate': False
        },
        'performance': {
            'handlers': ['file_performance'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# Log Level Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
if LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    LOG_LEVEL = 'INFO'

# Performance Monitoring Settings
PERFORMANCE_SETTINGS = {
    'track_commands': True,
    'track_news_fetch': True,
    'track_ai_analysis': True,
    'track_broadcasting': True,
    'log_slow_operations': True,
    'slow_operation_threshold': 5.0  # seconds
} 