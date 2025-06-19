#!/usr/bin/env python3
"""
Kripto Xəbər Botu Test Skripti
Botun funksiyalarını test etmək üçün
"""

import asyncio
import sys
import logging
from datetime import datetime

# Komponentləri import et
try:
    from config import TELEGRAM_BOT_TOKEN, NEWS_SOURCES, BOT_SETTINGS, GEMINI_API_KEY
    from news_fetcher import NewsFetcher, NewsItem
    from ai_analyzer import AIAnalyzer
    print("✅ Bütün modullar uğurla import edildi")
except ImportError as e:
    print(f"❌ Import xətası: {e}")
    sys.exit(1)

async def test_news_fetcher():
    """Xəbər çəkmə funksiyasını test edir"""
    print("\n🔍 Xəbər çəkmə test edilir...")
    
    fetcher = NewsFetcher()
    try:
        # Test üçün yalnız CoinDesk-dən xəbər çək
        news_list = await fetcher.fetch_coindesk_news()
        
        if news_list:
            print(f"✅ {len(news_list)} xəbər tapıldı")
            
            # İlk xəbəri göstər
            if news_list:
                news = news_list[0]
                print(f"📰 İlk xəbər: {news.title[:100]}...")
                print(f"🔗 URL: {news.url}")
                print(f"📅 Tarix: {news.published_date}")
        else:
            print("⚠️ Heç bir xəbər tapılmadı")
            
    except Exception as e:
        print(f"❌ Xəbər çəkmə xətası: {e}")
    finally:
        await fetcher.close_session()

async def test_ai_analyzer():
    """AI analiz funksiyasını test edir"""
    print("\n🧠 AI analiz test edilir...")
    
    analyzer = AIAnalyzer()
    
    # Test xəbəri
    test_news = NewsItem(
        title="Bitcoin Price Surges to New Heights",
        content="Bitcoin has reached a new all-time high today, driven by institutional investments and positive market sentiment.",
        url="https://example.com/bitcoin-news",
        source="Test Source",
        published_date=datetime.now()
    )
    
    try:
        analysis = await analyzer.analyze_news(test_news)
        if analysis:
            print("✅ AI analizi uğurla tamamlandı")
            print(f"📊 Analiz nəticəsi:\n{analysis}")
        else:
            print("⚠️ AI analizi boş nəticə qaytardı")
    except Exception as e:
        print(f"❌ AI analizi xətası: {e}")

def test_config():
    """Konfiqurasiya test edir"""
    print("\n⚙️ Konfiqurasiya test edilir...")
    
    # Token yoxlaması
    if TELEGRAM_BOT_TOKEN:
        print("✅ Telegram Bot Token təyin edilib")
    else:
        print("❌ Telegram Bot Token təyin edilməyib")
    
    # Xəbər mənbələri yoxlaması
    print(f"📰 Təyin edilən xəbər mənbələri: {len(NEWS_SOURCES)}")
    for source_name, source_config in NEWS_SOURCES.items():
        print(f"  • {source_name}: {source_config.get('name', 'N/A')}")
    
    # Bot parametrləri
    print(f"⏱️ Yoxlama intervalı: {BOT_SETTINGS['check_interval']} saniyə")
    print(f"📄 Maksimum xəbər: {BOT_SETTINGS['max_news_per_check']}")
    print(f"🤖 AI analizi: {'Aktiv' if BOT_SETTINGS['ai_analysis'] else 'Deaktiv'}")

async def run_tests():
    """Bütün testləri işlədir"""
    print("🧪 Kripto Xəbər Botu Test Prosesi Başlayır")
    print("=" * 50)
    
    # Konfiqurasiya testi
    test_config()
    
    # Xəbər çəkmə testi
    await test_news_fetcher()
    
    # AI analiz testi
    await test_ai_analyzer()
    
    print("\n" + "=" * 50)
    print("✅ Test prosesi tamamlandı!")
    print("\n📝 Bot işə salınmaq üçün:")
    print("1. .env faylında API key-ləri təyin edin")
    print("2. python main.py komandası ilə botu başladın")

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n🛑 Test prosesi dayandırıldı")
    except Exception as e:
        print(f"\n💥 Test xətası: {e}")
        sys.exit(1) 