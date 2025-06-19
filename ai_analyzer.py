import google.generativeai as genai
import logging
from typing import Optional, Dict
from config import GEMINI_API_KEY, AI_SETTINGS
from news_fetcher import NewsItem

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