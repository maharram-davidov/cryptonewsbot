import logging
import pytz
from datetime import datetime
from typing import List, Dict, Set
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, 
    CallbackContext, JobQueue
)
from telegram import ParseMode

from config import TELEGRAM_BOT_TOKEN, BOT_SETTINGS
from news_fetcher import NewsFetcher, NewsItem
from ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)

class CryptoNewsBot:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.news_fetcher = NewsFetcher()
        self.ai_analyzer = AIAnalyzer()
        self.updater = None
        self.subscribers: Set[int] = set()
        self.admin_users: Set[int] = set()
        self.last_news_check = datetime.now()

    def initialize(self):
        """Botu başladır (sync v13)"""
        if not self.token:
            raise ValueError("Telegram Bot Token təyin edilməyib!")
        
        self.updater = Updater(token=self.token, use_context=True)
        dispatcher = self.updater.dispatcher
        
        dispatcher.add_handler(CommandHandler("start", self.start_command))
        dispatcher.add_handler(CommandHandler("help", self.help_command))
        dispatcher.add_handler(CommandHandler("subscribe", self.subscribe_command))
        dispatcher.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        dispatcher.add_handler(CommandHandler("status", self.status_command))
        dispatcher.add_handler(CommandHandler("latest", self.latest_command))
        dispatcher.add_handler(CommandHandler("admin", self.admin_command))
        dispatcher.add_handler(CallbackQueryHandler(self.button_handler))
        
        job_queue = self.updater.job_queue
        if job_queue:
            job_queue.run_repeating(
                self.check_news_job,
                interval=BOT_SETTINGS['check_interval'],
                first=10
            )
            job_queue.run_daily(
                self.daily_cleanup_job,
                time=datetime.now().time().replace(hour=0, minute=0)
            )
            logger.info("Job queue konfiqurasiya edildi")
        else:
            logger.warning("JobQueue mövcud deyil")
        
        logger.info("Bot uğurla başladıldı")

    def start_command(self, update: Update, context: CallbackContext):
        """Start komandası (sync v13)"""
        user_id = update.effective_user.id
        welcome_text = f"""
🤖 **Kripto Xəbər Botu**

Salamlar! Mən sizə real-time kripto xəbərlərini AI analizi ilə birlikdə çatdırıram.

📰 **Xəbər Mənbələri:**
• CoinDesk
• The Block  
• Cointelegraph
• Crypto News
• NewsBTC

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
        update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    def help_command(self, update: Update, context: CallbackContext):
        """Kömək komandası (sync v13)"""
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
Admin: @your_telegram_username
"""
        update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    def subscribe_command(self, update: Update, context: CallbackContext):
        """Abunəlik komandası (sync v13)"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        if user_id in self.subscribers:
            update.message.reply_text("🔔 Siz artıq xəbər abunəçisisiniz!")
        else:
            self.subscribers.add(user_id)
            update.message.reply_text(
                f"✅ Təbriklər {user_name}! Artıq kripto xəbərləri alacaqsınız.\n\n"
                f"📊 Abunəçi sayı: {len(self.subscribers)}"
            )
            logger.info(f"Yeni abunəçi: {user_id} ({user_name})")

    def unsubscribe_command(self, update: Update, context: CallbackContext):
        """Abunəlikdən çıxış komandası (sync v13)"""
        user_id = update.effective_user.id
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            update.message.reply_text("❌ Abunəlikdən çıxdınız. İstədiyiniz vaxt yenidən abunə ola bilərsiniz.")
        else:
            update.message.reply_text("ℹ️ Siz artıq abunə deyilsiniz.")

    def status_command(self, update: Update, context: CallbackContext):
        """Status komandası (sync v13)"""
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
        update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

    def latest_command(self, update: Update, context: CallbackContext):
        """Son xəbərləri göstər (sync v13)"""
        update.message.reply_text("🔍 Son xəbərlər axtarılır...")
        try:
            news_list = self.news_fetcher.fetch_all_news()
            if not news_list:
                update.message.reply_text("📭 Hal-hazırda yeni xəbər yoxdur.")
                return
            for news in news_list[:3]:
                message = self.format_news_message(news)
                update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Latest komanda xətası: {e}")
            update.message.reply_text("❌ Xəbərlər yüklənərkən xəta baş verdi.")

    def admin_command(self, update: Update, context: CallbackContext):
        """Admin komandası (sync v13)"""
        from config import ADMIN_USER_IDS
        user_id = update.effective_user.id
        admin_ids = ADMIN_USER_IDS
        if user_id not in admin_ids:
            update.message.reply_text("⛔ Bu komanda yalnız adminlər üçündür.")
            return
        stats = self.news_fetcher.get_seen_news_stats()
        admin_text = f"""
🔐 **Admin Panel**

📊 **Statistika:**
👥 Abunəçilər: {len(self.subscribers)}
📰 Görülən xəbərlər (memory): {stats.get('total_seen', 0)}
💾 Fayl records: {stats.get('file_entries', 0)}

⚙️ **Konfiqurasiya:**
⏱️ Yoxlama intervalı: {BOT_SETTINGS['check_interval']}s
📄 Max xəbər: {BOT_SETTINGS['max_news_per_check']}
🤖 AI: {'ON' if BOT_SETTINGS['ai_analysis'] else 'OFF'}

🔍 **Son görülən xəbərlər:**"""
        
        for news in stats.get('recent_news', [])[:3]:
            admin_text += f"\n• {news['title']} ({news['source']})"
        
        admin_text += """

**Admin Komandaları:**
/broadcast <mesaj> - Bütün abunəçilərə mesaj
/stats - Ətraflı statistika
/cleanup - Manual temizlik
"""
        update.message.reply_text(admin_text, parse_mode=ParseMode.MARKDOWN)

    def button_handler(self, update: Update, context: CallbackContext):
        """Inline keyboard düymələrini idarə edir (sync v13)"""
        query = update.callback_query
        query.answer()
        
        # Callback query üçün update obyektini düzəlt
        if query.data == "subscribe":
            user_id = update.effective_user.id
            user_name = update.effective_user.first_name
            if user_id in self.subscribers:
                query.edit_message_text("🔔 Siz artıq xəbər abunəçisisiniz!")
            else:
                self.subscribers.add(user_id)
                query.edit_message_text(
                    f"✅ Təbriklər {user_name}! Artıq kripto xəbərləri alacaqsınız.\n\n"
                    f"📊 Abunəçi sayı: {len(self.subscribers)}"
                )
                logger.info(f"Yeni abunəçi: {user_id} ({user_name})")
        elif query.data == "latest":
            query.edit_message_text("🔍 Son xəbərlər axtarılır...")
            try:
                news_list = self.news_fetcher.fetch_all_news()
                if not news_list:
                    query.edit_message_text("📭 Hal-hazırda yeni xəbər yoxdur.")
                    return
                # İlk xəbəri göstər
                if news_list:
                    message = self.format_news_message(news_list[0])
                    query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                logger.error(f"Latest komanda xətası: {e}")
                query.edit_message_text("❌ Xəbərlər yüklənərkən xəta baş verdi.")
        elif query.data == "help":
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
Admin: @your_telegram_username
"""
            query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN)

    def check_news_job(self, context: CallbackContext):
        """Müntəzəm xəbər yoxlama işi (sync v13)"""
        try:
            logger.info("Xəbərlər yoxlanılır...")
            self.last_news_check = datetime.now()
            news_list = self.news_fetcher.fetch_all_news()
            if news_list and self.subscribers:
                for news in news_list[:BOT_SETTINGS['max_news_per_check']]:
                    message = self.format_news_message(news)
                    self.broadcast_message(message)
                logger.info(f"{len(news_list)} xəbər {len(self.subscribers)} abunəçiyə göndərildi")
        except Exception as e:
            logger.error(f"Xəbər yoxlama xətası: {e}")

    def daily_cleanup_job(self, context: CallbackContext):
        """Günlük temizlik işi (sync v13)"""
        try:
            self.news_fetcher.cleanup_seen_news(hours=24)
            logger.info("Günlük temizlik tamamlandı")
        except Exception as e:
            logger.error(f"Temizlik xətası: {e}")

    def format_news_message(self, news: NewsItem) -> str:
        """Xəbər mesajını formatlaşdırır (sync v13)"""
        try:
            analysis = ""
            if BOT_SETTINGS['ai_analysis']:
                analysis = self.ai_analyzer.analyze_news(news)
                if analysis:
                    analysis = f"\n\n🧠 **AI Analizi:**\n{analysis}"
            source_emoji = {
                'CoinDesk': '📰',
                'The Block': '🔷',
                'Cointelegraph': '📊',
                'Crypto News': '🌐',
                'NewsBTC': '₿'
            }.get(news.source, '📰')
            
            # Azərbaycan saatına çevirmək
            utc_time = news.published_date.replace(tzinfo=pytz.UTC)
            azerbaijan_tz = pytz.timezone('Asia/Baku')
            local_time = utc_time.astimezone(azerbaijan_tz)
            
            message = f"""
{source_emoji} **{news.title}**

📍 Mənbə: {news.source}
🕐 Tarix: {local_time.strftime('%d.%m.%Y %H:%M')} (AZT)

🔗 [Ətraflı oxu]({news.url}){analysis}

---
"""
            return message.strip()
        except Exception as e:
            logger.error(f"Mesaj formatlaşdırma xətası: {e}")
            return f"📰 **{news.title}**\n🔗 [Link]({news.url})"

    def broadcast_message(self, message: str):
        """Bütün abunəçilərə mesaj göndərir (sync v13)"""
        failed_sends = []
        for user_id in self.subscribers.copy():
            try:
                self.updater.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.warning(f"User {user_id} göndərim xətası: {e}")
                failed_sends.append(user_id)
        for user_id in failed_sends:
            if user_id in self.subscribers:
                self.subscribers.remove(user_id)
                logger.info(f"User {user_id} abunəlikdən çıxarıldı (göndərim xətası)")

    def start_bot(self):
        """Botu başladır (sync v13)"""
        self.initialize()
        logger.info("Bot başladılır...")
        self.updater.start_polling()
        self.updater.idle()