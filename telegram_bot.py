import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Set
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, JobQueue
)
from telegram.constants import ParseMode

from config import TELEGRAM_BOT_TOKEN, BOT_SETTINGS
from news_fetcher import NewsFetcher, NewsItem
from ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

class CryptoNewsBot:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.news_fetcher = NewsFetcher()
        self.ai_analyzer = AIAnalyzer()
        self.application = None
        self.subscribers: Set[int] = set()
        self.admin_users: Set[int] = set()
        self.last_news_check = datetime.now()
        
    async def initialize(self):
        """Botu başladır"""
        if not self.token:
            raise ValueError("Telegram Bot Token təyin edilməyib!")
            
        # Application yaradır
        self.application = Application.builder().token(self.token).build()
        
        # Komanda handler-lərini əlavə edir
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("latest", self.latest_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Job queue-nu konfiqurasiya edir
        job_queue = self.application.job_queue
        job_queue.run_repeating(
            self.check_news_job,
            interval=BOT_SETTINGS['check_interval'],
            first=10
        )
        
        # Günlük temizlik işi
        job_queue.run_daily(
            self.daily_cleanup_job,
            time=datetime.now().time().replace(hour=0, minute=0)
        )
        
        logger.info("Bot uğurla başladıldı")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start komandası"""
        user_id = update.effective_user.id
        welcome_text = f"""
🤖 **Kripto Xəbər Botu**

Salamlar! Mən sizə real-time kripto xəbərlərini AI analizi ilə birlikdə çatdırıram.

📰 **Xəbər Mənbələri:**
• CoinDesk
• CryptoPanic  
• Cointelegraph

🧠 **AI Analizi:**
• Market təsiri (Bullish/Bearish/Neytral)
• Risk səviyyəsi
• Qısa yorum

**Komandalar:**
/subscribe - Xəbər abunəliyini aktivləşdir
/unsubscribe - Abunəliyi dayandır
/latest - Son xəbərləri göstər
/status - Bot statusu
/help - Kömək

Bot istifadəyə hazırdır! ✨
"""
        
        keyboard = [
            [InlineKeyboardButton("📰 Abunə ol", callback_data="subscribe")],
            [InlineKeyboardButton("📊 Son xəbərlər", callback_data="latest")],
            [InlineKeyboardButton("ℹ️ Kömək", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kömək komandası"""
        help_text = """
📚 **Bot Komandaları**

🔹 `/start` - Botu başlat
🔹 `/subscribe` - Xəbər abunəliyini aktivləşdir
🔹 `/unsubscribe` - Abunəliyi dayandır
🔹 `/latest` - Son 5 xəbəri göstər
🔹 `/status` - Bot statusu və statistika
🔹 `/help` - Bu kömək mətnini göstər

**Xəbər Formatı:**
📰 Başlıq
🔗 Link
📊 AI Analizi:
  • Market təsiri
  • Risk səviyyəsi
  • Qısa yorum

**Problemlər üçün əlaqə:**
Admin: @davudov07
"""
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Abunəlik komandası"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        if user_id in self.subscribers:
            await update.message.reply_text("🔔 Siz artıq xəbər abunəçisisiniz!")
        else:
            self.subscribers.add(user_id)
            await update.message.reply_text(
                f"✅ Təbriklər {user_name}! Artıq kripto xəbərləri alacaqsınız.\n\n"
                f"📊 Abunəçi sayı: {len(self.subscribers)}"
            )
            logger.info(f"Yeni abunəçi: {user_id} ({user_name})")
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Abunəlikdən çıxış komandası"""
        user_id = update.effective_user.id
        
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            await update.message.reply_text("❌ Abunəlikdən çıxdınız. İstədiyiniz vaxt yenidən abunə ola bilərsiniz.")
        else:
            await update.message.reply_text("ℹ️ Siz artıq abunə deyilsiniz.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status komandası"""
        status_text = f"""
📊 **Bot Statusu**

👥 Abunəçi sayı: {len(self.subscribers)}
🕐 Son yoxlama: {self.last_news_check.strftime('%H:%M:%S')}
⚙️ Yoxlama intervalı: {BOT_SETTINGS['check_interval']} saniyə
🔍 Maksimum xəbər: {BOT_SETTINGS['max_news_per_check']}
🤖 AI analizi: {'Aktiv' if BOT_SETTINGS['ai_analysis'] else 'Deaktiv'}

**Mənbələr:**
📰 CoinDesk - RSS
📰 The Block - RSS
📰 Cointelegraph - RSS
📰 Crypto News - RSS
📰 NewsBTC - RSS

Bot normal işləyir ✅
"""
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
    
    async def latest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Son xəbərləri göstər"""
        await update.message.reply_text("🔍 Son xəbərlər axtarılır...")
        
        try:
            news_list = await self.news_fetcher.fetch_all_news()
            
            if not news_list:
                await update.message.reply_text("📭 Hal-hazırda yeni xəbər yoxdur.")
                return
            
            # İlk 3 xəbəri göstər
            for news in news_list[:3]:
                message = await self.format_news_message(news)
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
                await asyncio.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Latest komanda xətası: {e}")
            await update.message.reply_text("❌ Xəbərlər yüklənərkən xəta baş verdi.")
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin komandası"""
        from config import ADMIN_USER_IDS
        user_id = update.effective_user.id
        
        # Sadə admin yoxlaması (daha güclü yoxlama lazımdır)
        admin_ids = ADMIN_USER_IDS
        
        if user_id not in admin_ids:
            await update.message.reply_text("⛔ Bu komanda yalnız adminlər üçündür.")
            return
        
        admin_text = f"""
🔐 **Admin Panel**

📊 **Statistika:**
👥 Abunəçilər: {len(self.subscribers)}
📰 Görülən xəbərlər: {len(self.news_fetcher.seen_news)}

⚙️ **Konfiqurasiya:**
⏱️ Yoxlama intervalı: {BOT_SETTINGS['check_interval']}s
📄 Max xəbər: {BOT_SETTINGS['max_news_per_check']}
🤖 AI: {'ON' if BOT_SETTINGS['ai_analysis'] else 'OFF'}

**Admin Komandaları:**
/broadcast <mesaj> - Bütün abunəçilərə mesaj
/stats - Ətraflı statistika
/cleanup - Manual temizlik
"""
        await update.message.reply_text(admin_text, parse_mode=ParseMode.MARKDOWN)
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inline keyboard düymələrini idarə edir"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "subscribe":
            await self.subscribe_command(update, context)
        elif query.data == "latest":
            await self.latest_command(update, context)
        elif query.data == "help":
            await self.help_command(update, context)
    
    async def check_news_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Müntəzəm xəbər yoxlama işi"""
        try:
            logger.info("Xəbərlər yoxlanılır...")
            self.last_news_check = datetime.now()
            
            # Yeni xəbərləri çəkir
            news_list = await self.news_fetcher.fetch_all_news()
            
            if news_list and self.subscribers:
                # İlk bir neçə xəbəri abunəçilərə göndərir
                for news in news_list[:BOT_SETTINGS['max_news_per_check']]:
                    message = await self.format_news_message(news)
                    await self.broadcast_message(message)
                    await asyncio.sleep(2)  # Rate limiting
                    
                logger.info(f"{len(news_list)} xəbər {len(self.subscribers)} abunəçiyə göndərildi")
            
        except Exception as e:
            logger.error(f"Xəbər yoxlama xətası: {e}")
    
    async def daily_cleanup_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Günlük temizlik işi"""
        try:
            self.news_fetcher.cleanup_seen_news(hours=24)
            logger.info("Günlük temizlik tamamlandı")
        except Exception as e:
            logger.error(f"Temizlik xətası: {e}")
    
    async def format_news_message(self, news: NewsItem) -> str:
        """Xəbər mesajını formatlaşdırır"""
        try:
            # AI analizi
            analysis = ""
            if BOT_SETTINGS['ai_analysis']:
                analysis = await self.ai_analyzer.analyze_news(news)
                if analysis:
                    analysis = f"\n\n🧠 **AI Analizi:**\n{analysis}"
            
            # Emoji seçir
            source_emoji = {
                'CoinDesk': '📰',
                'The Block': '🔷',
                'Cointelegraph': '📊',
                'Crypto News': '🌐',
                'NewsBTC': '₿'
            }.get(news.source, '📰')
            
            message = f"""
{source_emoji} **{news.title}**

📍 Mənbə: {news.source}
🕐 Tarix: {news.published_date.strftime('%d.%m.%Y %H:%M')}

🔗 [Ətraflı oxu]({news.url}){analysis}

---
"""
            return message.strip()
            
        except Exception as e:
            logger.error(f"Mesaj formatlaşdırma xətası: {e}")
            return f"📰 **{news.title}**\n🔗 [Link]({news.url})"
    
    async def broadcast_message(self, message: str):
        """Bütün abunəçilərə mesaj göndərir"""
        failed_sends = []
        
        for user_id in self.subscribers.copy():
            try:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                await asyncio.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"User {user_id} göndərim xətası: {e}")
                failed_sends.append(user_id)
        
        # Uğursuz göndərimləri temizlə
        for user_id in failed_sends:
            if user_id in self.subscribers:
                self.subscribers.remove(user_id)
                logger.info(f"User {user_id} abunəlikdən çıxarıldı (göndərim xətası)")
    
    async def start_bot(self):
        """Botu başladır"""
        try:
            await self.initialize()
            logger.info("Bot başladılır...")
            
            await self.application.run_polling(
                poll_interval=1.0,
                timeout=10,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"Bot başlatma xətası: {e}")
            raise
        finally:
            await self.news_fetcher.close_session()
    
    async def stop_bot(self):
        """Botu dayandırır"""
        if self.application:
            await self.application.stop()
        await self.news_fetcher.close_session()
        logger.info("Bot dayandırıldı") 