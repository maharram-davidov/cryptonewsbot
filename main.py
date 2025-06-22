#!/usr/bin/env python3
"""
Kripto Xəbər Botu - Ana Fayl
AI ilə kripto xəbərləri analiz edən Telegram bot
"""

import logging
import sys
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from bot import CryptoNewsBot

# Enhanced logging configuration
def setup_logging():
    """Comprehensive logging configuration"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | Line:%(lineno)-4d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation (main log)
    file_handler = RotatingFileHandler(
        'logs/crypto_bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/crypto_bot_errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Performance log handler
    perf_handler = RotatingFileHandler(
        'logs/performance.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=2,
        encoding='utf-8'
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(simple_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Create performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.propagate = False
    
    # Log startup info
    logging.info("="*80)
    logging.info("🚀 STARTUP: Kripto Xəbər Botu logging system initialized")
    logging.info(f"📅 STARTUP: Boot time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"🐍 STARTUP: Python version: {sys.version}")
    logging.info(f"📁 STARTUP: Working directory: {os.getcwd()}")
    logging.info("="*80)

def log_system_info():
    """Log system and environment information"""
    logger = logging.getLogger(__name__)
    
    try:
        import platform
        import psutil
        
        logger.info("💻 SYSTEM_INFO: Gathering system information")
        logger.info(f"🖥️  SYSTEM: OS: {platform.system()} {platform.release()}")
        logger.info(f"🖥️  SYSTEM: Architecture: {platform.architecture()[0]}")
        logger.info(f"🖥️  SYSTEM: Processor: {platform.processor()}")
        logger.info(f"💾 MEMORY: Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
        logger.info(f"💾 MEMORY: Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB")
        logger.info(f"💽 STORAGE: Free disk space: {psutil.disk_usage('.').free / (1024**3):.1f} GB")
        
    except ImportError:
        logger.warning("⚠️  SYSTEM_INFO: psutil not available, skipping detailed system info")
    except Exception as e:
        logger.error(f"💥 SYSTEM_INFO: Error gathering system info: {e}")

def main():
    """Main application entry point with comprehensive error handling"""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🎯 MAIN: Application startup initiated")
        
        # Log system information
        log_system_info()
        
        # Check environment
        logger.info("🔧 MAIN: Checking environment configuration")
        
        # Import and check config
        try:
            from config import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, BOT_SETTINGS
            
            if not TELEGRAM_BOT_TOKEN:
                logger.error("💥 CONFIG: TELEGRAM_BOT_TOKEN not found in environment")
                raise ValueError("Telegram Bot Token not configured")
            
            logger.info("✅ CONFIG: Telegram Bot Token found")
            
            if GEMINI_API_KEY:
                logger.info("✅ CONFIG: Gemini API Key found - AI features enabled")
            else:
                logger.warning("⚠️  CONFIG: Gemini API Key not found - AI features disabled")
            
            logger.info(f"⚙️  CONFIG: Check interval: {BOT_SETTINGS['check_interval']}s")
            logger.info(f"⚙️  CONFIG: Max news per check: {BOT_SETTINGS['max_news_per_check']}")
            logger.info(f"⚙️  CONFIG: AI analysis: {'enabled' if BOT_SETTINGS['ai_analysis'] else 'disabled'}")
            
        except ImportError as e:
            logger.error(f"💥 CONFIG: Failed to import configuration: {e}")
            raise
        
        # Initialize and start bot
        logger.info("🤖 MAIN: Initializing CryptoNewsBot")
        bot = CryptoNewsBot()
        
        logger.info("🚀 MAIN: Starting bot service")
        logger.info("🎉 MAIN: Bot is now running! Press Ctrl+C to stop")
        
        bot.start_bot()
        
    except KeyboardInterrupt:
        logger.info("🛑 MAIN: Bot stopped by user (Ctrl+C)")
        logger.info("👋 MAIN: Graceful shutdown completed")
    except Exception as e:
        logger.error(f"💥 MAIN: Critical error during bot execution: {e}")
        logger.error(f"📍 MAIN: Traceback: {sys.exc_info()}")
        
        # Try to log additional context
        try:
            import traceback
            logger.error(f"📍 MAIN: Full traceback:\n{traceback.format_exc()}")
        except:
            pass
        
        sys.exit(1)
    finally:
        logger.info("🔚 MAIN: Application shutdown sequence completed")
        logger.info("="*80)

if __name__ == '__main__':
    main()

