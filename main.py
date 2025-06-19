#!/usr/bin/env python3
"""
Kripto Xəbər Botu - Ana Fayl
AI ilə kripto xəbərləri analiz edən Telegram bot
"""

import logging
import sys
from datetime import datetime
from bot import CryptoNewsBot

# Logging konfiqurasiyası
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('crypto_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        logger.info("🤖 Kripto Xəbər Botu başladılır...")
        logger.info(f"📅 Başlatma vaxtı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        bot = CryptoNewsBot()
        bot.start_bot()
    except KeyboardInterrupt:
        logger.info("🔴 Bot əl ilə dayandırıldı")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

