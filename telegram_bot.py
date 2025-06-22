import asyncio
import logging
import json
import os
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
        self.subscribers_file = 'subscribers.json'
        self.user_settings_file = 'user_settings.json'
        self.user_settings: Dict[int, Dict] = {}
        
        # Başlangıçta subscribe verilerini yükle
        self._load_subscribers()
        self._load_user_settings()
        
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
        """Kullanıcı ayarlarını JSON dosyasından yükler"""
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
        """Kullanıcı ayarlarını JSON dosyasına kaydet"""
        try:
            # Int key'leri string'e çevir JSON için
            data = {str(k): v for k, v in self.user_settings.items()}
            with open(self.user_settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 {len(self.user_settings)} kullanıcı ayarı saxlanıldı")
        except Exception as e:
            logger.error(f"Kullanıcı ayarları saxlama xətası: {e}")
    
    def _get_user_settings(self, user_id: int) -> Dict:
        """Kullanıcının ayarlarını getirir, yoksa varsayılan ayarları döndürür"""
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
        """Kullanıcının belirli ayarını günceller"""
        settings = self._get_user_settings(user_id)
        settings[setting_key] = value
        settings['last_activity'] = datetime.now().isoformat()
        self.user_settings[user_id] = settings
        self._save_user_settings()
    
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
        self.application.add_handler(CommandHandler("reset_news", self.reset_news_command))
        self.application.add_handler(CommandHandler("daily_summary", self.manual_daily_summary_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
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
        
        # Günlük özet işi (gece 00:00'da)
        job_queue.run_daily(
            self.daily_summary_job,
            time=datetime.now().time().replace(hour=0, minute=5)  # 00:05'te çalışır
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
🔹 `/settings` - Bildirim ayarlarını dəyişdir
🔹 `/help` - Bu kömək mətnini göstər

**Admin Komandaları:**
🔸 `/reset_news` - Görülən xəbərləri təmizlə (köhnə xəbər problemini həll edir)
🔸 `/daily_summary` - Manual günlük özet göndər

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
            self._save_subscribers()  # Dosyaya kaydet
            await update.message.reply_text(
                f"✅ Təbriklər {user_name}! Artıq kripto xəbərləri alacaqsınız.\n\n"
                f"📊 Abunəçi sayı: {len(self.subscribers)}\n"
                f"💾 Abunəlik saxlanıldı!"
            )
            logger.info(f"Yeni abunəçi: {user_id} ({user_name})")
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Abunəlikdən çıxış komandası"""
        user_id = update.effective_user.id
        
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            self._save_subscribers()  # Dosyaya kaydet
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
💾 Subscribe faylı: {'✅ Mövcud' if os.path.exists(self.subscribers_file) else '❌ Yoxdur'}

**Mənbələr:**
📰 CoinDesk - RSS
📰 The Block - RSS
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
    
    async def reset_news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Görülən xəbərləri reset etmək komandası (yalnız admin)"""
        from config import ADMIN_USER_IDS
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_USER_IDS:
            await update.message.reply_text("❌ Bu komandaya icazəniz yoxdur.")
            return
        
        await update.message.reply_text("🚨 Görülən xəbər məlumatları təmizlənir...")
        
        try:
            # Emergency reset et
            success = self.news_fetcher.emergency_reset_seen_news()
            
            if success:
                # Statistika al
                stats = self.news_fetcher.get_seen_news_stats()
                
                message = f"""
🚨 **EMERGENCY RESET TƏMİZLİK**

✅ Bütün görülən xəbər məlumatları təmizləndi!

📊 **Yeni Durum:**
• Görülən xəbərlər: {stats.get('total_seen', 0)}
• Yaddaş cache: Təmizləndi
• Fayl: Yenidən yaradıldı

⚠️ **Nəticə:** 
İndi bot yalnız YENİ xəbərləri göndərəcək.
Köhnə xəbərlər bir daha gəlməyəcək.

✨ Sistem hazırdır!
"""
                await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
                logger.warning(f"🚨 Admin {user_id} tərəfindən emergency reset edildi")
            else:
                await update.message.reply_text("❌ Reset zamanı xəta baş verdi. Log-lara baxın.")
                
        except Exception as e:
            logger.error(f"Reset komanda xətası: {e}")
            await update.message.reply_text("❌ Reset komandası işləmədi. Texniki xəta.")
    
    async def manual_daily_summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manuel günlük özet komandası (admin)"""
        from config import ADMIN_USER_IDS
        user_id = update.effective_user.id
        
        if user_id not in ADMIN_USER_IDS:
            await update.message.reply_text("❌ Bu komandaya icazəniz yoxdur.")
            return
        
        await update.message.reply_text("🔍 Günlük özet hazırlanır... (Bu bir neçə saniyə süre bilər)")
        
        try:
            # Günlük özet işini manuel çalıştır
            if not self.subscribers:
                await update.message.reply_text("⚠️ Abunəçi yoxdur, özet göndərilmədi.")
                return
            
            # Son 24 saatın xəbərlərini al
            last_24h_news = self.news_fetcher.get_last_24_hours_news()
            
            if not last_24h_news:
                summary_message = f"""📅 **MANUEL GÜNLÜK ÖZET**
🕐 Tarix: {datetime.now().strftime('%d.%m.%Y %H:%M')}

📭 Son 24 saatda kripto bazarında önemli xəbər tapılmadı.

🔧 Admin tərəfindən manuel göndərildi."""
            else:
                # AI ile özet hazırla
                summary = await self.ai_analyzer.generate_daily_summary(last_24h_news)
                
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
            
            # Günlük özet açık olan abunəçilərə özeti göndər
            await self.broadcast_daily_summary(summary_message)
            
            # Günlük özet alan kullanıcı sayısını hesapla
            daily_users = [uid for uid in self.subscribers 
                          if self._get_user_settings(uid).get('daily_summary', True)]
            
            await update.message.reply_text(
                f"✅ Manuel günlük özet {len(daily_users)} kullanıcıya göndərildi!\n"
                f"📊 Analiz edilən xəbər sayı: {len(last_24h_news)}\n"
                f"👥 Günlük özet açık olan: {len(daily_users)}/{len(self.subscribers)}"
            )
            
            logger.info(f"🔧 Admin {user_id} tərəfindən manuel günlük özet göndərildi")
            
        except Exception as e:
            logger.error(f"Manuel günlük özet xətası: {e}")
            await update.message.reply_text("❌ Manuel günlük özet hazırlanarkən xəta baş verdi.")

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kullanıcı ayarları menüsü"""
        user_id = update.effective_user.id
        
        if user_id not in self.subscribers:
            await update.message.reply_text(
                "⚠️ Ayarları dəyişdirmək üçün əvvəlcə abunə olmalısınız!\n\n"
                "📰 /subscribe komandası ilə abunə ola bilərsiniz."
            )
            return
        
        settings = self._get_user_settings(user_id)
        
        # Ayar durumlarına göre emoji ve text
        instant_status = "🔔 AÇIQ" if settings['instant_notifications'] else "🔕 BAĞLI"
        daily_status = "📅 AÇIQ" if settings['daily_summary'] else "❌ BAĞLI"
        
        settings_text = f"""⚙️ **BİLDİRİM AYARLARI**

👤 **İstifadəçi:** {update.effective_user.first_name}
📊 **Abunəlik statusu:** Aktiv

🔔 **Anlık Xəbərlər:** {instant_status}
   • Real-time kripto xəbərləri
   • Gün ərzində gələn yeniliklər

📅 **Günlük Özet:** {daily_status}  
   • Hər gecə saat 00:05'tə
   • AI ilə hazırlanan günün özeti

**💡 İpucu:** Anlık xəbərləri bağlasanız da günlük özet almağa davam edə bilərsiniz!"""

        # Inline keyboard
        keyboard = [
            [InlineKeyboardButton(
                f"🔔 Anlık Xəbərlər: {instant_status}", 
                callback_data=f"toggle_instant_{user_id}"
            )],
            [InlineKeyboardButton(
                f"📅 Günlük Özet: {daily_status}", 
                callback_data=f"toggle_daily_{user_id}"
            )],
            [InlineKeyboardButton("🔄 Yenilə", callback_data=f"refresh_settings_{user_id}")],
            [InlineKeyboardButton("⬅️ Geri", callback_data="back_to_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

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
            # Inline button üçün subscribe işlemi
            user_id = update.effective_user.id
            user_name = update.effective_user.first_name
            
            if user_id in self.subscribers:
                await query.edit_message_text("🔔 Siz artıq xəbər abunəçisisiniz!")
            else:
                self.subscribers.add(user_id)
                self._save_subscribers()  # Dosyaya kaydet
                await query.edit_message_text(
                    f"✅ Təbriklər {user_name}! Artıq kripto xəbərləri alacaqsınız.\n\n"
                    f"📊 Abunəçi sayı: {len(self.subscribers)}\n"
                    f"💾 Abunəlik saxlanıldı!"
                )
                logger.info(f"Yeni abunəçi (button): {user_id} ({user_name})")
        elif query.data == "latest":
            await self.latest_command(update, context)
        elif query.data == "help":
            await self.help_command(update, context)
        elif query.data == "settings":
            await self.handle_settings_callback(update, context)
        elif query.data.startswith("toggle_instant_"):
            await self.handle_toggle_instant(update, context)
        elif query.data.startswith("toggle_daily_"):
            await self.handle_toggle_daily(update, context)
        elif query.data.startswith("refresh_settings_"):
            await self.handle_refresh_settings(update, context)
        elif query.data == "back_to_main":
            await self.handle_back_to_main(update, context)
    
    async def handle_settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Settings button callback'i"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        if user_id not in self.subscribers:
            await query.edit_message_text(
                "⚠️ Ayarları dəyişdirmək üçün əvvəlcə abunə olmalısınız!\n\n"
                "📰 /subscribe komandası ilə abunə ola bilərsiniz."
            )
            return
        
        settings = self._get_user_settings(user_id)
        
        # Ayar durumlarına göre emoji ve text
        instant_status = "🔔 AÇIQ" if settings['instant_notifications'] else "🔕 BAĞLI"
        daily_status = "📅 AÇIQ" if settings['daily_summary'] else "❌ BAĞLI"
        
        settings_text = f"""⚙️ **BİLDİRİM AYARLARI**

👤 **İstifadəçi:** {update.effective_user.first_name}
📊 **Abunəlik statusu:** Aktiv

🔔 **Anlık Xəbərlər:** {instant_status}
   • Real-time kripto xəbərləri
   • Gün ərzində gələn yeniliklər

📅 **Günlük Özet:** {daily_status}  
   • Hər gecə saat 00:05'tə
   • AI ilə hazırlanan günün özeti

**💡 İpucu:** Anlık xəbərləri bağlasanız da günlük özet almağa davam edə bilərsiniz!"""

        # Inline keyboard
        keyboard = [
            [InlineKeyboardButton(
                f"🔔 Anlık Xəbərlər: {instant_status}", 
                callback_data=f"toggle_instant_{user_id}"
            )],
            [InlineKeyboardButton(
                f"📅 Günlük Özet: {daily_status}", 
                callback_data=f"toggle_daily_{user_id}"
            )],
            [InlineKeyboardButton("🔄 Yenilə", callback_data=f"refresh_settings_{user_id}")],
            [InlineKeyboardButton("⬅️ Geri", callback_data="back_to_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_toggle_instant(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Anlık bildirim ayarını aç/kapat"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        settings = self._get_user_settings(user_id)
        new_value = not settings['instant_notifications']
        self._update_user_setting(user_id, 'instant_notifications', new_value)
        
        status_text = "açıldı 🔔" if new_value else "bağlandı 🔕"
        await query.answer(f"Anlık xəbərlər {status_text}")
        
        # Settings menüsünü yenile
        await self.handle_refresh_settings(update, context)
    
    async def handle_toggle_daily(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Günlük özet ayarını aç/kapat"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        settings = self._get_user_settings(user_id)
        new_value = not settings['daily_summary']
        self._update_user_setting(user_id, 'daily_summary', new_value)
        
        status_text = "açıldı 📅" if new_value else "bağlandı ❌"
        await query.answer(f"Günlük özet {status_text}")
        
        # Settings menüsünü yenile
        await self.handle_refresh_settings(update, context)
    
    async def handle_refresh_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Settings menüsünü yenile"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        settings = self._get_user_settings(user_id)
        
        # Ayar durumlarına göre emoji ve text
        instant_status = "🔔 AÇIQ" if settings['instant_notifications'] else "🔕 BAĞLI"
        daily_status = "📅 AÇIQ" if settings['daily_summary'] else "❌ BAĞLI"
        
        settings_text = f"""⚙️ **BİLDİRİM AYARLARI**

👤 **İstifadəçi:** {update.effective_user.first_name}
📊 **Abunəlik statusu:** Aktiv

🔔 **Anlık Xəbərlər:** {instant_status}
   • Real-time kripto xəbərləri
   • Gün ərzində gələn yeniliklər

📅 **Günlük Özet:** {daily_status}  
   • Hər gecə saat 00:05'tə
   • AI ilə hazırlanan günün özeti

**💡 İpucu:** Anlık xəbərləri bağlasanız da günlük özet almağa davam edə bilərsiniz!"""

        # Inline keyboard
        keyboard = [
            [InlineKeyboardButton(
                f"🔔 Anlık Xəbərlər: {instant_status}", 
                callback_data=f"toggle_instant_{user_id}"
            )],
            [InlineKeyboardButton(
                f"📅 Günlük Özet: {daily_status}", 
                callback_data=f"toggle_daily_{user_id}"
            )],
            [InlineKeyboardButton("🔄 Yenilə", callback_data=f"refresh_settings_{user_id}")],
            [InlineKeyboardButton("⬅️ Geri", callback_data="back_to_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_back_to_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ana menüye geri dön"""
        query = update.callback_query
        
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
/settings - Bildirim ayarları
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
        
        await query.edit_message_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

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
                    await self.broadcast_instant_news(message)  # Anlık haber gönderme
                    await asyncio.sleep(2)  # Rate limiting
                    
                # Instant notifications açık olan kullanıcı sayısını logla
                instant_users = [uid for uid in self.subscribers 
                               if self._get_user_settings(uid).get('instant_notifications', True)]
                logger.info(f"{len(news_list)} xəbər {len(instant_users)} anlık bildirim kullanıcısına göndərildi")
            
        except Exception as e:
            logger.error(f"Xəbər yoxlama xətası: {e}")
    
    async def daily_cleanup_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Günlük temizlik işi"""
        try:
            self.news_fetcher.cleanup_seen_news(hours=24)
            logger.info("Günlük temizlik tamamlandı")
        except Exception as e:
            logger.error(f"Temizlik xətası: {e}")
    
    async def daily_summary_job(self, context: ContextTypes.DEFAULT_TYPE):
        """Günlük özet işi - gece 00:05'te son 24 saatın xəbərlərini özetləyir"""
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
                # AI ile özet hazırla
                summary = await self.ai_analyzer.generate_daily_summary(last_24h_news)
                
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
            
            # Günlük özet açık olan abunəçilərə özeti göndər
            await self.broadcast_daily_summary(summary_message)
            
            # Günlük özet alan kullanıcı sayısını logla
            daily_users = [uid for uid in self.subscribers 
                          if self._get_user_settings(uid).get('daily_summary', True)]
            logger.info(f"✅ Günlük özet {len(daily_users)} kullanıcıya göndərildi")
            
        except Exception as e:
            logger.error(f"Günlük özet işi xətası: {e}")
            
            # Xəta mesajı
            error_message = f"""🚨 **GÜNLÜK ÖZET XƏTAsi**
🕐 Tarix: {datetime.now().strftime('%d.%m.%Y')}

❌ Günlük özet hazırlanarkən texniki xəta baş verdi.
🔧 Sistem yenidən cəhd edəcək.

Admin məlumatlandırıldı."""
            
            try:
                await self.broadcast_message(error_message)
            except:
                pass
    
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
        
        # Uğursuz göndərimləri temizlə ve dosyaya kaydet
        if failed_sends:
            for user_id in failed_sends:
                if user_id in self.subscribers:
                    self.subscribers.remove(user_id)
                    logger.info(f"User {user_id} abunəlikdən çıxarıldı (göndərim xətası)")
            self._save_subscribers()  # Güncel listeyi dosyaya kaydet
    
    async def broadcast_instant_news(self, message: str):
        """Anlık bildirim açık olan kullanıcılara haber gönderir"""
        failed_sends = []
        sent_count = 0
        
        for user_id in self.subscribers.copy():
            settings = self._get_user_settings(user_id)
            
            # Sadece instant notifications açık olanlara gönder
            if settings.get('instant_notifications', True):
                try:
                    await self.application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )
                    sent_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"User {user_id} anlık göndərim xətası: {e}")
                    failed_sends.append(user_id)
        
        # Uğursuz göndərimləri temizlə
        if failed_sends:
            for user_id in failed_sends:
                if user_id in self.subscribers:
                    self.subscribers.remove(user_id)
                    logger.info(f"User {user_id} abunəlikdən çıxarıldı (göndərim xətası)")
            self._save_subscribers()
        
        logger.info(f"Anlık xəbər {sent_count} kullanıcıya göndərildi")
    
    async def broadcast_daily_summary(self, message: str):
        """Günlük özet açık olan kullanıcılara özet gönderir"""
        failed_sends = []
        sent_count = 0
        
        for user_id in self.subscribers.copy():
            settings = self._get_user_settings(user_id)
            
            # Sadece daily summary açık olanlara gönder
            if settings.get('daily_summary', True):
                try:
                    await self.application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True
                    )
                    sent_count += 1
                    await asyncio.sleep(0.1)  # Rate limiting
                    
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
        
        logger.info(f"Günlük özet {sent_count} kullanıcıya göndərildi")
    
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