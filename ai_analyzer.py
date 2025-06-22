import google.generativeai as genai
import logging
from typing import Optional, Dict, List
from config import GEMINI_API_KEY, AI_SETTINGS
from news_fetcher import NewsItem
from datetime import datetime

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(AI_SETTINGS['model'])
        else:
            logger.warning("Gemini API key təyin edilməyib")
            self.model = None
            
    def analyze_news(self, news_item: NewsItem) -> Optional[str]:
        """Xəbəri AI ilə analiz edir (sync)"""
        try:
            if not self.model:
                return self._fallback_analysis(news_item)
            
            # Xəbər məzmununu hazırlayır
            news_content = f"""
Başlıq: {news_item.title}
Mənbə: {news_item.source}
Məzmun: {news_item.content[:500]}
URL: {news_item.url}
"""
            
            # AI promptunu hazırlayır
            prompt = AI_SETTINGS['analysis_prompt'].format(news_content=news_content)
            
            # Gemini API çağırır
            response = self._call_gemini(prompt)
            
            if response:
                return response
            else:
                return self._fallback_analysis(news_item)
                
        except Exception as e:
            logger.error(f"AI analiz xətası: {e}")
            return self._fallback_analysis(news_item)
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Gemini API-ni sync çağırır"""
        try:
            system_prompt = "Siz kripto xəbərlərini analiz edən mütəxəssissiniz. Azərbaycan dilində cavab verin."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=AI_SETTINGS['max_tokens'],
                    temperature=AI_SETTINGS['temperature']
                )
            )
            
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                return None
            
        except Exception as e:
            logger.error(f"Gemini API xətası: {e}")
            return None
    
    def _fallback_analysis(self, news_item: NewsItem) -> str:
        """AI əlçatmaz olduqda əsas analiz"""
        try:
            title_lower = news_item.title.lower()
            content_lower = news_item.content.lower()
            
            # Açar sözlərə əsasən analiz
            bullish_keywords = [
                'rise', 'surge', 'pump', 'bull', 'green', 'gain', 'profit', 
                'moon', 'rocket', 'adoption', 'partnership', 'investment',
                'yüksəliş', 'artım', 'qazanc', 'tərəqqi', 'inkişaf'
            ]
            
            bearish_keywords = [
                'fall', 'drop', 'crash', 'bear', 'red', 'loss', 'dump',
                'decline', 'down', 'fear', 'sell', 'panic',
                'düşüş', 'azalma', 'itki', 'tənəzzül', 'böhran'
            ]
            
            neutral_keywords = [
                'stable', 'sideways', 'consolidation', 'analysis', 'report',
                'update', 'news', 'announcement', 'study',
                'sabit', 'hesabat', 'yenilənmə', 'elan'
            ]
            
            # Skor hesablayır
            bullish_score = sum(1 for word in bullish_keywords if word in title_lower or word in content_lower)
            bearish_score = sum(1 for word in bearish_keywords if word in title_lower or word in content_lower)
            neutral_score = sum(1 for word in neutral_keywords if word in title_lower or word in content_lower)
            
            # Market təsirini müəyyən edir
            if bullish_score > bearish_score and bullish_score > neutral_score:
                market_impact = "Bullish"
                risk_level = "Orta"
                analysis = "Xəbər kripto bazarı üçün müsbət siqnallar göndərir."
            elif bearish_score > bullish_score and bearish_score > neutral_score:
                market_impact = "Bearish"
                risk_level = "Yüksək"
                analysis = "Xəbər bazarda mənfi təsir göstərə bilər."
            else:
                market_impact = "Neytral"
                risk_level = "Aşağı"
                analysis = "Xəbər bazarda əhəmiyyətli dəyişikliyə səbəb olmaya bilər."
            
            return f"""🔥 Market Təsiri: {market_impact}
📊 Analiz: {analysis}
⚠️ Risk: {risk_level}"""
            
        except Exception as e:
            logger.error(f"Fallback analiz xətası: {e}")
            return "📊 Analiz hazırlanarkən xəta baş verdi."
    
    def analyze_sentiment_keywords(self, text: str) -> Dict[str, int]:
        """Mətnin əhval-ruhiyyəsini açar sözlərə görə analiz edir"""
        positive_keywords = [
            'good', 'great', 'excellent', 'positive', 'growth', 'increase',
            'success', 'win', 'benefit', 'opportunity', 'promising',
            'yaxşı', 'əla', 'müsbət', 'böyümə', 'artım', 'uğur'
        ]
        
        negative_keywords = [
            'bad', 'terrible', 'negative', 'decrease', 'loss', 'fail',
            'problem', 'issue', 'concern', 'risk', 'danger',
            'pis', 'mənfi', 'azalma', 'itki', 'problem', 'risk'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        return {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': max(0, len(text.split()) - positive_count - negative_count)
        } 
    
    async def generate_daily_summary(self, news_list: List[NewsItem]) -> Optional[str]:
        """Son 24 saatın xəbərlərindən günlük özet hazırlayır"""
        try:
            if not self.model:
                return self._fallback_daily_summary(news_list)
            
            if not news_list:
                return "📭 Son 24 saatda yeni xəbər tapılmadı."
            
            # Xəbər siyahısını AI üçün formatla
            news_content = "Son 24 saatın kripto xəbərləri:\n\n"
            for i, news in enumerate(news_list, 1):
                news_content += f"{i}. Başlıq: {news.title}\n"
                news_content += f"   Mənbə: {news.source}\n"
                news_content += f"   Məzmun: {news.content[:300]}...\n"
                news_content += f"   URL: {news.url}\n\n"
            
            # Günlük özet prompt-u
            daily_prompt = f"""
Siz kripto xəbərlərini analiz edən mütəxəssissiniz. Aşağıdakı son 24 saatın xəbərlərini analiz edib Azərbaycan dilində ətraflı günlük özet hazırlayın:

{news_content}

📋 **GÜNLÜK ÖZET FORMAT:**
📅 Tarix: [Bugünün tarixi]
📊 Ümumi Bazar Durumu: [Bullish/Bearish/Neytral]

🔥 **ÖNƏMLİ XƏBƏRLƏR:**
• [En önemli 3-5 haberi özetle]

📈 **BAZAR ANALİZİ:**
• Market trend-i
• Risk seviyyesi
• Yatırım tavsiyesi

⚠️ **DİQQƏT MƏRKƏZLƏRI:**
• Önemli gelişmeler
• Gelecek beklentiler

🎯 **QISA NƏTICƏ:**
[1-2 cümlede günün özeti]

Lütfen xəbərləri önem derecesine göre sıralayın və sadece ÖNEMLİ olanları əhatə edin. Çok uzun yazmayın - maksimum 800 kelime.
"""
            
            # AI analysis çağır
            response = self._call_gemini(daily_prompt)
            
            if response:
                return response
            else:
                return self._fallback_daily_summary(news_list)
                
        except Exception as e:
            logger.error(f"Günlük özet AI xətası: {e}")
            return self._fallback_daily_summary(news_list)
    
    def _fallback_daily_summary(self, news_list: List[NewsItem]) -> str:
        """AI əlçatmaz olduqda əsas günlük özet"""
        try:
            if not news_list:
                return "📭 Son 24 saatda yeni xəbər tapılmadı."
            
            # Haberleri kaynaklara göre grupla
            source_groups = {}
            bullish_count = 0
            bearish_count = 0
            
            for news in news_list:
                source = news.source
                if source not in source_groups:
                    source_groups[source] = []
                source_groups[source].append(news)
                
                # Basit sentiment analizi
                title_lower = news.title.lower()
                if any(word in title_lower for word in ['rise', 'surge', 'gain', 'up', 'bull']):
                    bullish_count += 1
                elif any(word in title_lower for word in ['fall', 'drop', 'down', 'bear', 'crash']):
                    bearish_count += 1
            
            # Market durumunu belirle
            if bullish_count > bearish_count:
                market_mood = "📈 Bullish"
            elif bearish_count > bullish_count:
                market_mood = "📉 Bearish"
            else:
                market_mood = "➡️ Neytral"
            
            # Özet oluştur
            summary = f"""📅 **GÜNLÜK XƏBƏRLƏRİN ÖZETİ**
🕐 Tarix: {datetime.now().strftime('%d.%m.%Y')}
📊 Ümumi Durum: {market_mood}
📰 Ümumi Xəbər Sayı: {len(news_list)}

🔥 **MƏNBƏLƏRƏ GÖRƏ BÖLGÜ:**"""
            
            for source, source_news in source_groups.items():
                summary += f"\n• {source}: {len(source_news)} xəbər"
            
            summary += f"""

📈 **ÖNƏMLİ XƏBƏRLƏR:**"""
            
            # İlk 5 haberi özetle
            for i, news in enumerate(news_list[:5], 1):
                summary += f"\n{i}. {news.title[:80]}..."
                summary += f"\n   📍 {news.source}"
            
            summary += f"""

🎯 **QISA NƏTİCƏ:**
Son 24 saatda {len(news_list)} xəbər analiz edildi. Bazar {market_mood.lower()} əhval-ruhiyyə göstərir.

---
🤖 Ətraflı AI analizi üçün sistem yenidən cəhd edəcək."""
            
            return summary
            
        except Exception as e:
            logger.error(f"Fallback günlük özet xətası: {e}")
            return "❌ Günlük özet hazırlanarkən xəta baş verdi."
            