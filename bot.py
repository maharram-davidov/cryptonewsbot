import logging
import json
import os
import pytz
import time
import traceback
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

# Enhanced logging setup
logger = logging.getLogger(__name__)

# Performance tracking for sync version
class PerformanceTracker:
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str) -> str:
        timer_id = f"{operation}_{time.time()}"
        self.metrics[timer_id] = time.time()
        return timer_id
    
    def end_timer(self, timer_id: str, operation: str, user_id: int = None):
        if timer_id in self.metrics:
            duration = time.time() - self.metrics[timer_id]
            user_info = f" [User: {user_id}]" if user_id else ""
            logger.info(f"⏱️ PERFORMANCE: {operation} completed in {duration:.2f}s{user_info}")
            del self.metrics[timer_id]
            return duration
        return None

performance = PerformanceTracker()

class CryptoNewsBot:
    def __init__(self):
        logger.info("🚀 SYSTEM: CryptoNewsBot (sync) initialization started")
        
        self.token = TELEGRAM_BOT_TOKEN
        self.news_fetcher = NewsFetcher()
        self.ai_analyzer = AIAnalyzer()
        self.updater = None
        self.subscribers: Set[int] = set()
        self.admin_users: Set[int] = set()
        self.last_news_check = datetime.now()
        self.subscribers_file = 'subscribers.json'
        self.user_settings_file = 'user_settings.json'
        self.user_settings: Dict[int, Dict] = {}
        
        # Statistics tracking
        self.stats = {
            'total_commands': 0,
            'total_news_sent': 0,
            'total_errors': 0,
            'startup_time': datetime.now(),
            'last_restart': datetime.now()
        }
        
        logger.info("📊 SYSTEM: Bot statistics initialized (sync version)")
        
        # Başlangıçta subscribe verilerini yükle
        self._load_subscribers()
        self._load_user_settings()
        
        logger.info("✅ SYSTEM: CryptoNewsBot (sync) initialization completed successfully")
        
    def _log_user_action(self, user_id: int, action: str, details: str = "", success: bool = True):
        """Kullanıcı aktivitelerini detaylı loglar (sync)"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        timestamp = datetime.now().strftime("%H:%M:%S")
        logger.info(f"👤 USER_ACTION [{timestamp}]: User {user_id} - {action} - {status} {details}")
        
        # İstatistikleri güncelle
        if success:
            self.stats['total_commands'] += 1
    
    def _log_system_event(self, event_type: str, message: str, level: str = "info"):
        """Sistem olaylarını loglar (sync)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"🔧 SYSTEM [{timestamp}]: {event_type} - {message}"
        
        if level == "error":
            logger.error(log_message)
            self.stats['total_errors'] += 1
        elif level == "warning":
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _load_subscribers(self):
        """Subscribe verilerini JSON dosyasından yükler"""
        try:
            if os.path.exists(self.subscribers_file):
                with open(self.subscribers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.subscribers = set(data.get('subscribers', []))
                    logger.info(f"📂 {len(self.subscribers)} abunəçi yükləndi")
            else:
                logger.info("📂 Subscribe faylı tapılmadı, yeni fayl yaradılacaq")
        except Exception as e:
            logger.error(f"Subscribe fayl yükləmə xətası: {e}")
            self.subscribers = set()
    
    def _save_subscribers(self):
        """Subscribe verilerini JSON dosyasına saxlayır"""
        try:
            data = {
                'subscribers': list(self.subscribers),
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.subscribers)
            }
            with open(self.subscribers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 {len(self.subscribers)} abunəçi faylda saxlanıldı")
        except Exception as e:
            logger.error(f"Subscribe fayl saxlama xətası: {e}")
    
    def _load_user_settings(self):
        """Kullanıcı ayarlarını JSON dosyasından yükler (sync)"""
        try:
            if os.path.exists(self.user_settings_file):
                with open(self.user_settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # String key'leri int'e çevir
                    self.user_settings = {int(k): v for k, v in data.items()}
                    logger.info(f"⚙️ {len(self.user_settings)} kullanıcı ayarı yükləndi")
            else:
                logger.info("⚙️ Kullanıcı ayarları faylı tapılmadı, yeni yaradılacaq")
                self.user_settings = {}
        except Exception as e:
            logger.error(f"Kullanıcı ayarları yükləmə xətası: {e}")
            self.user_settings = {}
    
    def _save_user_settings(self):
        """Kullanıcı ayarlarını JSON dosyasına kaydet (sync)"""
        try:
            # Int key'leri string'e çevir JSON için
            data = {str(k): v for k, v in self.user_settings.items()}
            with open(self.user_settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 {len(self.user_settings)} kullanıcı ayarı saxlanıldı")
        except Exception as e:
            logger.error(f"Kullanıcı ayarları saxlama xətası: {e}")
    
    def _get_user_settings(self, user_id: int) -> Dict:
        """Kullanıcının ayarlarını getirir, yoksa varsayılan ayarları döndürür (sync)"""
        default_settings = {
            'instant_notifications': True,  # Anlık haberler açık
            'daily_summary': True,         # Günlük özet açık
            'joined_date': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        if user_id not in self.user_settings:
            self.user_settings[user_id] = default_settings.copy()
            self._save_user_settings()
        
        return self.user_settings[user_id]

    def _update_user_setting(self, user_id: int, setting_key: str, value: bool):
        """Kullanıcının belirli ayarını günceller (sync)"""
        settings = self._get_user_settings(user_id)
        settings[setting_key] = value
        settings['last_activity'] = datetime.now().isoformat()
        self.user_settings[user_id] = settings
        self._save_user_settings()

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
        dispatcher.add_handler(CommandHandler("daily_summary", self.manual_daily_summary_command))
        dispatcher.add_handler(CommandHandler("settings", self.settings_command))
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
            
            # Günlük özet işi (gece 00:05'te)
            job_queue.run_daily(
                self.daily_summary_job,
                time=datetime.now().time().replace(hour=0, minute=5)
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
            [InlineKeyboardButton("⚙️ Ayarlar", callback_data="settings")],
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
            self._save_subscribers()  # Dosyaya kaydet
            update.message.reply_text(
                f"✅ Təbriklər {user_name}! Artıq kripto xəbərləri alacaqsınız.\n\n"
                f"📊 Abunəçi sayı: {len(self.subscribers)}\n"
                f"💾 Abunəlik saxlanıldı!"
            )
            logger.info(f"Yeni abunəçi: {user_id} ({user_name})")

    def unsubscribe_command(self, update: Update, context: CallbackContext):
        """Abunəlikdən çıxış komandası (sync v13)"""
        user_id = update.effective_user.id
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            self._save_subscribers()  # Dosyaya kaydet
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
        
        # Kullanıcı ayar istatistikleri
        instant_enabled = sum(1 for settings in self.user_settings.values() if settings.get('instant_notifications', True))
        daily_enabled = sum(1 for settings in self.user_settings.values() if settings.get('daily_summary', True))
        
        admin_text = f"""
🔐 **Admin Panel**

📊 **Statistika:**
👥 Abunəçilər: {len(self.subscribers)}
⚙️ Settings olan kullanıcılar: {len(self.user_settings)}
🔔 Instant notifications: {instant_enabled}
📅 Daily summary: {daily_enabled}
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
/daily_summary - Manuel günlük özet
/stats - Ətraflı statistika
/cleanup - Manual temizlik
"""
        update.message.reply_text(admin_text, parse_mode=ParseMode.MARKDOWN)

    def settings_command(self, update: Update, context: CallbackContext):
        """Kullanıcı ayarları komandası (sync v13)"""
        user_id = update.effective_user.id
        user_settings = self._get_user_settings(user_id)
        
        # Ayar durumları için emoji
        instant_status = "🔔" if user_settings['instant_notifications'] else "🔕"
        daily_status = "📅" if user_settings['daily_summary'] else "📭"
        
        settings_text = f"""⚙️ **KULLANICI AYARLARI**

{instant_status} **Anlık Xəbərlər**
{instant_status} Durum: {'Açık' if user_settings['instant_notifications'] else 'Kapalı'}
📝 Kripto xəbərləri dərhal sizə göndərilsin

{daily_status} **Günlük Özet**  
{daily_status} Durum: {'Açık' if user_settings['daily_summary'] else 'Kapalı'}
📝 Hər gecə saat 00:05'da günlük özet alın

---
✨ Bu ayarları aşağıdaki düymələrlə dəyişə bilərsiniz"""

        keyboard = [
            [InlineKeyboardButton(
                f"🔔 Anlık Xəbərlər: {'✅' if user_settings['instant_notifications'] else '❌'}", 
                callback_data="toggle_instant"
            )],
            [InlineKeyboardButton(
                f"📅 Günlük Özet: {'✅' if user_settings['daily_summary'] else '❌'}", 
                callback_data="toggle_daily"
            )],
            [InlineKeyboardButton("🔄 Yenilə", callback_data="refresh_settings")],
            [InlineKeyboardButton("🔙 Ana menü", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

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
                self._save_subscribers()  # Dosyaya kaydet
                query.edit_message_text(
                    f"✅ Təbriklər {user_name}! Artıq kripto xəbərləri alacaqsınız.\n\n"
                    f"📊 Abunəçi sayı: {len(self.subscribers)}\n"
                    f"💾 Abunəlik saxlanıldı!"
                )
                logger.info(f"Yeni abunəçi (button): {user_id} ({user_name})")
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
🔹 `/settings` - Bildirim ayarları
🔹 `/help` - Bu kömək mətnini göstər

**Xəbər Formatı:**
📰 Başlıq
🔗 Link
📊 AI Analizi:
  • Market təsiri
  • Risk səviyyəsi
  • Qısa yorum

**Problemlər üçün əlaqə:**
Admin: @davudov.07
"""
            query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN)
        elif query.data == "settings":
            self.handle_settings_callback(update, context)
        elif query.data == "toggle_instant":
            self.handle_toggle_instant(update, context)
        elif query.data == "toggle_daily":
            self.handle_toggle_daily(update, context)
        elif query.data == "refresh_settings":
            self.handle_refresh_settings(update, context)
        elif query.data == "back_to_main":
            self.handle_back_to_main(update, context)

    def handle_settings_callback(self, update: Update, context: CallbackContext):
        """Settings callback handler (sync v13)"""
        query = update.callback_query
        query.answer()
        
        user_id = update.effective_user.id
        user_settings = self._get_user_settings(user_id)
        
        # Ayar durumları için emoji
        instant_status = "🔔" if user_settings['instant_notifications'] else "🔕"
        daily_status = "📅" if user_settings['daily_summary'] else "📭"
        
        settings_text = f"""⚙️ **KULLANICI AYARLARI**

{instant_status} **Anlık Xəbərlər**
{instant_status} Durum: {'Açık' if user_settings['instant_notifications'] else 'Kapalı'}
📝 Kripto xəbərləri dərhal sizə göndərilsin

{daily_status} **Günlük Özet**  
{daily_status} Durum: {'Açık' if user_settings['daily_summary'] else 'Kapalı'}
📝 Hər gecə saat 00:05'da günlük özet alın

---
✨ Bu ayarları aşağıdaki düymələrlə dəyişə bilərsiniz"""

        keyboard = [
            [InlineKeyboardButton(
                f"🔔 Anlık Xəbərlər: {'✅' if user_settings['instant_notifications'] else '❌'}", 
                callback_data="toggle_instant"
            )],
            [InlineKeyboardButton(
                f"📅 Günlük Özet: {'✅' if user_settings['daily_summary'] else '❌'}", 
                callback_data="toggle_daily"
            )],
            [InlineKeyboardButton("🔄 Yenilə", callback_data="refresh_settings")],
            [InlineKeyboardButton("🔙 Ana menü", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    def handle_toggle_instant(self, update: Update, context: CallbackContext):
        """Anlık haber ayarını toggle eder (sync v13)"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Mevcut ayarı al ve tersine çevir
        current_setting = self._get_user_settings(user_id)['instant_notifications']
        new_setting = not current_setting
        
        # Ayarı güncelle
        self._update_user_setting(user_id, 'instant_notifications', new_setting)
        
        status_text = "açıldı ✅" if new_setting else "kapatıldı ❌"
        query.answer(f"🔔 Anlık xəbərlər {status_text}")
        
        # Settings menüsünü yenile
        self.handle_refresh_settings(update, context)

    def handle_toggle_daily(self, update: Update, context: CallbackContext):
        """Günlük özet ayarını toggle eder (sync v13)"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Mevcut ayarı al ve tersine çevir
        current_setting = self._get_user_settings(user_id)['daily_summary']
        new_setting = not current_setting
        
        # Ayarı güncelle
        self._update_user_setting(user_id, 'daily_summary', new_setting)
        
        status_text = "açıldı ✅" if new_setting else "kapatıldı ❌"
        query.answer(f"📅 Günlük özet {status_text}")
        
        # Settings menüsünü yenile
        self.handle_refresh_settings(update, context)

    def handle_refresh_settings(self, update: Update, context: CallbackContext):
        """Settings menüsünü yeniler (sync v13)"""
        query = update.callback_query
        user_id = update.effective_user.id
        user_settings = self._get_user_settings(user_id)
        
        # Ayar durumları için emoji
        instant_status = "🔔" if user_settings['instant_notifications'] else "🔕"
        daily_status = "📅" if user_settings['daily_summary'] else "📭"
        
        settings_text = f"""⚙️ **KULLANICI AYARLARI**

{instant_status} **Anlık Xəbərlər**
{instant_status} Durum: {'Açık' if user_settings['instant_notifications'] else 'Kapalı'}
📝 Kripto xəbərləri dərhal sizə göndərilsin

{daily_status} **Günlük Özet**  
{daily_status} Durum: {'Açık' if user_settings['daily_summary'] else 'Kapalı'}
📝 Hər gecə saat 00:05'da günlük özet alın

---
✨ Bu ayarları aşağıdaki düymələrlə dəyişə bilərsiniz"""

        keyboard = [
            [InlineKeyboardButton(
                f"🔔 Anlık Xəbərlər: {'✅' if user_settings['instant_notifications'] else '❌'}", 
                callback_data="toggle_instant"
            )],
            [InlineKeyboardButton(
                f"📅 Günlük Özet: {'✅' if user_settings['daily_summary'] else '❌'}", 
                callback_data="toggle_daily"
            )],
            [InlineKeyboardButton("🔄 Yenilə", callback_data="refresh_settings")],
            [InlineKeyboardButton("🔙 Ana menü", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    def handle_back_to_main(self, update: Update, context: CallbackContext):
        """Ana menüye geri döner (sync v13)"""
        query = update.callback_query
        query.answer()
        
        welcome_text = f"""
🤖 **Kripto Xəbər Botu**

Salamlar! Mən sizə real-time kripto xəbərlərini AI analizi ilə birlikdə çatdırıram.

📰 **Xəbər Mənbələri:**
• CoinDesk
• The Block  
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
            [InlineKeyboardButton("⚙️ Ayarlar", callback_data="settings")],
            [InlineKeyboardButton("ℹ️ Kömək", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    def check_news_job(self, context: CallbackContext):
        """Müntəzəm xəbər yoxlama işi (sync v13)"""
        try:
            logger.info("Xəbərlər yoxlanılır...")
            self.last_news_check = datetime.now()
            news_list = self.news_fetcher.fetch_all_news()
            if news_list and self.subscribers:
                for news in news_list[:BOT_SETTINGS['max_news_per_check']]:
                    message = self.format_news_message(news)
                    self.broadcast_instant_news(message)  # Akıllı broadcast kullan
                logger.info(f"{len(news_list)} xəbər instant_news kullanıcılarına göndərildi")
        except Exception as e:
            logger.error(f"Xəbər yoxlama xətası: {e}")

    def daily_cleanup_job(self, context: CallbackContext):
        """Günlük temizlik işi (sync v13)"""
        try:
            self.news_fetcher.cleanup_seen_news(hours=24)
            logger.info("Günlük temizlik tamamlandı")
        except Exception as e:
            logger.error(f"Temizlik xətası: {e}")
    
    def daily_summary_job(self, context: CallbackContext):
        """Günlük özet işi - gece 00:05'te son 24 saatın xəbərlərini özetləyir (sync v13)"""
        try:
            if not self.subscribers:
                logger.info("Günlük özet: Abunəçi yoxdur, özet göndərilmədi")
                return
            
            logger.info("🌙 Günlük özet hazırlanır...")
            
            # Son 24 saatın xəbərlərini al
            last_24h_news = self.news_fetcher.get_last_24_hours_news()
            
            if not last_24h_news:
                summary_message = """📅 **GÜNLÜK ÖZET**
🕐 Tarix: {date}

📭 Son 24 saatda kripto bazarında önemli xəbər tapılmadı.

🌙 Sabaha qədər sakit gecə! ✨""".format(date=datetime.now().strftime('%d.%m.%Y'))
            else:
                # AI ile özet hazırla (sync versiyonda async çalışmaz, fallback kullan)
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    summary = loop.run_until_complete(self.ai_analyzer.generate_daily_summary(last_24h_news))
                except:
                    summary = self.ai_analyzer._fallback_daily_summary(last_24h_news)
                
                if summary:
                    summary_message = f"""🌙 **GÜNLÜK XƏBƏRLƏRİN ÖZETİ**

{summary}

---
🤖 Bu özet AI tərəfindən hazırlanıb
🕐 Göndərilmə vaxtı: {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
                else:
                    summary_message = """📅 **GÜNLÜK ÖZET**
🕐 Tarix: {date}

❌ AI özet sistemində texniki xəta baş verdi.
📰 Son 24 saatda {count} xəbər qeydə alındı.

🔧 Sistemimiz düzəlişə çalışacaq.""".format(
                        date=datetime.now().strftime('%d.%m.%Y'),
                        count=len(last_24h_news)
                    )
            
            # Günlük özet isteyenlere özeti göndər
            self.broadcast_daily_summary(summary_message)
            
            logger.info(f"✅ Günlük özet {len(self.subscribers)} abunəçiyə göndərildi")
            
        except Exception as e:
            logger.error(f"Günlük özet işi xətası: {e}")
            
            # Xəta mesajı
            error_message = f"""🚨 **GÜNLÜK ÖZET XƏTAsi**
🕐 Tarix: {datetime.now().strftime('%d.%m.%Y')}

❌ Günlük özet hazırlanarkən texniki xəta baş verdi.
🔧 Sistem yenidən cəhd edəcək.

Admin məlumatlandırıldı."""
            
            try:
                self.broadcast_daily_summary(error_message)
            except:
                pass

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
        
        # Uğursuz göndərimləri temizlə ve dosyaya kaydet
        if failed_sends:
            for user_id in failed_sends:
                if user_id in self.subscribers:
                    self.subscribers.remove(user_id)
                    logger.info(f"User {user_id} abunəlikdən çıxarıldı (göndərim xətası)")
            self._save_subscribers()  # Güncel listeyi dosyaya kaydet

    def broadcast_instant_news(self, message: str):
        """Sadəcə anlık xəbər istəyən abunəçilərə göndərir (sync v13)"""
        failed_sends = []
        sent_count = 0
        
        for user_id in self.subscribers.copy():
            # Kullanıcının instant notification ayarını kontrol et
            user_settings = self._get_user_settings(user_id)
            if not user_settings.get('instant_notifications', True):
                continue  # Bu kullanıcı anlık haber istemiyor, atla
                
            try:
                self.updater.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"User {user_id} anlık xəbər göndərim xətası: {e}")
                failed_sends.append(user_id)
        
        # Uğursuz göndərimləri temizlə
        if failed_sends:
            for user_id in failed_sends:
                if user_id in self.subscribers:
                    self.subscribers.remove(user_id)
                    logger.info(f"User {user_id} abunəlikdən çıxarıldı (göndərim xətası)")
            self._save_subscribers()
        
        logger.info(f"📰 Anlık xəbər {sent_count} istəkli kullanıcıya göndərildi")

    def broadcast_daily_summary(self, message: str):
        """Sadəcə günlük özet istəyən abunəçilərə göndərir (sync v13)"""
        failed_sends = []
        sent_count = 0
        
        for user_id in self.subscribers.copy():
            # Kullanıcının daily summary ayarını kontrol et
            user_settings = self._get_user_settings(user_id)
            if not user_settings.get('daily_summary', True):
                continue  # Bu kullanıcı günlük özet istemiyor, atla
                
            try:
                self.updater.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"User {user_id} günlük özet göndərim xətası: {e}")
                failed_sends.append(user_id)
        
        # Uğursuz göndərimləri temizlə
        if failed_sends:
            for user_id in failed_sends:
                if user_id in self.subscribers:
                    self.subscribers.remove(user_id)
                    logger.info(f"User {user_id} abunəlikdən çıxarıldı (göndərim xətası)")
            self._save_subscribers()
        
        logger.info(f"📅 Günlük özet {sent_count} istəkli kullanıcıya göndərildi")

    def manual_daily_summary_command(self, update: Update, context: CallbackContext):
        """Manuel günlük özet komandası (admin - sync v13)"""
        from config import ADMIN_USER_IDS
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_USER_IDS:
            update.message.reply_text("❌ Bu komandaya icazəniz yoxdur.")
            return
        
        update.message.reply_text("🔍 Günlük özet hazırlanır... (Bu bir neçə saniyə süre bilər)")
        
        try:
            # Günlük özet işini manuel çalıştır
            if not self.subscribers:
                update.message.reply_text("⚠️ Abunəçi yoxdur, özet göndərilmədi.")
                return
            
            # Son 24 saatın xəbərlərini al
            last_24h_news = self.news_fetcher.get_last_24_hours_news()
            
            if not last_24h_news:
                summary_message = f"""📅 **MANUEL GÜNLÜK ÖZET**
🕐 Tarix: {datetime.now().strftime('%d.%m.%Y %H:%M')}

📭 Son 24 saatda kripto bazarında önemli xəbər tapılmadı.

🔧 Admin tərəfindən manuel göndərildi."""
            else:
                # AI ile özet hazırla (sync versiyonda async çalışmaz, fallback kullan)
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    summary = loop.run_until_complete(self.ai_analyzer.generate_daily_summary(last_24h_news))
                except:
                    summary = self.ai_analyzer._fallback_daily_summary(last_24h_news)
                
                if summary:
                    summary_message = f"""📋 **MANUEL GÜNLÜK ÖZET**

{summary}

---
🤖 Bu özet AI tərəfindən hazırlanıb
🔧 Admin tərəfindən manuel göndərildi
🕐 Göndərilmə vaxtı: {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
                else:
                    summary_message = f"""📅 **MANUEL GÜNLÜK ÖZET**
🕐 Tarix: {datetime.now().strftime('%d.%m.%Y %H:%M')}

❌ AI özet sistemində texniki xəta baş verdi.
📰 Son 24 saatda {len(last_24h_news)} xəbər qeydə alındı.

🔧 Admin tərəfindən manuel göndərildi."""
            
            # Günlük özet isteyenlere özeti göndər
            self.broadcast_daily_summary(summary_message)
            
            update.message.reply_text(
                f"✅ Manuel günlük özet {len(self.subscribers)} abunəçiyə göndərildi!\n"
                f"📊 Analiz edilən xəbər sayı: {len(last_24h_news)}"
            )
            
            logger.info(f"🔧 Admin {user_id} tərəfindən manuel günlük özet göndərildi")
            
        except Exception as e:
            logger.error(f"Manuel günlük özet xətası: {e}")
            update.message.reply_text("❌ Manuel günlük özet hazırlanarkən xəta baş verdi.")

    def start_bot(self):
        """Botu başladır (sync v13)"""
        self.initialize()
        logger.info("Bot başladılır...")
        self.updater.start_polling()
        self.updater.idle()