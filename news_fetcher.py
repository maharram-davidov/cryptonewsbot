import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import json
import os
from typing import List, Dict, Optional
from config import NEWS_SOURCES

logger = logging.getLogger(__name__)

class NewsItem:
    def __init__(self, title: str, content: str, url: str, source: str, 
                 published_date: datetime, summary: str = ""):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.published_date = published_date
        self.summary = summary
        # URL-ə və başlığa əsaslanan unikal hash
        self.hash = abs(hash(f"{title.strip().lower()}{url}"))

    def __eq__(self, other):
        return isinstance(other, NewsItem) and self.hash == other.hash

    def __hash__(self):
        return self.hash
    
    def to_dict(self):
        """Xəbəri dictionary formatına çevirir"""
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date.isoformat(),
            'hash': self.hash
        }

class NewsFetcher:
    def __init__(self):
        self.seen_news_file = 'seen_news.json'
        self.seen_news = set()
        self._load_seen_news()

    def _load_seen_news(self):
        """Əvvəlcədən görülən xəbərləri fayldan yükləyir"""
        try:
            if os.path.exists(self.seen_news_file):
                with open(self.seen_news_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Hash və tarix məlumatlarını yükləyir
                    current_time = datetime.now()
                    cutoff_time = current_time - timedelta(hours=24)
                    
                    for item in data:
                        try:
                            # Yalnız son 24 saat ərzindəki xəbərləri saxlayır
                            saved_at = datetime.fromisoformat(item.get('saved_at', item.get('published_date')))
                            if saved_at > cutoff_time:
                                self.seen_news.add(item['hash'])
                        except Exception as e:
                            logger.warning(f"Xəbər item yüklənmə xətası: {e}")
                            continue
                            
                logger.info(f"{len(self.seen_news)} əvvəlki xəbər yükləndi")
        except Exception as e:
            logger.error(f"Görülən xəbərlər yüklənmə xətası: {e}")
            self.seen_news = set()

    def _save_seen_news(self, news_item: NewsItem = None):
        """Görülən xəbərləri fayla saxlayır"""
        try:
            # Mövcud məlumatları yükləyir
            existing_data = []
            if os.path.exists(self.seen_news_file):
                try:
                    with open(self.seen_news_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = []
            
            # Yeni xəbər əlavə edir
            if news_item:
                new_entry = {
                    'hash': news_item.hash,
                    'title': news_item.title[:100],  # İlk 100 simvol
                    'source': news_item.source,
                    'url': news_item.url,
                    'published_date': news_item.published_date.isoformat(),
                    'saved_at': datetime.now().isoformat()
                }
                
                # Dublikatları yoxlayır
                if not any(item['hash'] == news_item.hash for item in existing_data):
                    existing_data.append(new_entry)
            
            # Son 24 saat ərzindəki xəbərləri filtr edir
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=24)
            
            filtered_data = []
            for item in existing_data:
                try:
                    saved_at = datetime.fromisoformat(item['saved_at'])
                    if saved_at > cutoff_time:
                        filtered_data.append(item)
                except:
                    continue
            
            # Faylı yazar
            with open(self.seen_news_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"{len(filtered_data)} xəbər hash-i saxlanıldı")
        except Exception as e:
            logger.error(f"Görülən xəbərlər saxlama xətası: {e}")

    def _is_news_seen(self, news_item: NewsItem) -> bool:
        """Xəbərin əvvəlcədən görüldüyünü yoxlayır"""
        return news_item.hash in self.seen_news

    def _mark_news_as_seen(self, news_item: NewsItem):
        """Xəbəri görüldü olaraq işarələyir"""
        self.seen_news.add(news_item.hash)
        self._save_seen_news(news_item)

    def fetch_coindesk_news(self) -> List[NewsItem]:
        try:
            news_items = []
            source_config = NEWS_SOURCES['coindesk']
            feed = feedparser.parse(source_config['rss_url'])
            for entry in feed.entries[:10]:
                try:
                    title = entry.title
                    url = entry.link
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    published = datetime(*entry.published_parsed[:6])
                    if published > datetime.now() - timedelta(days=1):
                        content = self._fetch_article_content(url)
                        news_item = NewsItem(
                            title=title,
                            content=content,
                            url=url,
                            source=source_config['name'],
                            published_date=published,
                            summary=summary
                        )
                        if not self._is_news_seen(news_item):
                            news_items.append(news_item)
                            self._mark_news_as_seen(news_item)
                except Exception as e:
                    logger.error(f"CoinDesk xəbər emal xətası: {e}")
            return news_items
        except Exception as e:
            logger.error(f"CoinDesk RSS xətası: {e}")
            return []

    def fetch_theblock_news(self) -> List[NewsItem]:
        try:
            news_items = []
            source_config = NEWS_SOURCES['theblock']
            feed = feedparser.parse(source_config['rss_url'])
            for entry in feed.entries[:10]:
                try:
                    title = entry.title
                    url = entry.link
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    published = datetime(*entry.published_parsed[:6])
                    if published > datetime.now() - timedelta(days=1):
                        content = self._fetch_article_content(url)
                        news_item = NewsItem(
                            title=title,
                            content=content,
                            url=url,
                            source=source_config['name'],
                            published_date=published,
                            summary=summary
                        )
                        if not self._is_news_seen(news_item):
                            news_items.append(news_item)
                            self._mark_news_as_seen(news_item)
                except Exception as e:
                    logger.error(f"The Block xəbər emal xətası: {e}")
            return news_items
        except Exception as e:
            logger.error(f"The Block RSS xətası: {e}")
            return []

    def fetch_cointelegraph_news(self) -> List[NewsItem]:
        try:
            news_items = []
            source_config = NEWS_SOURCES['cointelegraph']
            feed = feedparser.parse(source_config['rss_url'])
            for entry in feed.entries[:10]:
                try:
                    title = entry.title
                    url = entry.link
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    published = datetime(*entry.published_parsed[:6])
                    if published > datetime.now() - timedelta(days=1):
                        content = self._fetch_article_content(url)
                        news_item = NewsItem(
                            title=title,
                            content=content,
                            url=url,
                            source=source_config['name'],
                            published_date=published,
                            summary=summary
                        )
                        if not self._is_news_seen(news_item):
                            news_items.append(news_item)
                            self._mark_news_as_seen(news_item)
                except Exception as e:
                    logger.error(f"Cointelegraph xəbər emal xətası: {e}")
            return news_items
        except Exception as e:
            logger.error(f"Cointelegraph RSS xətası: {e}")
            return []

    def _fetch_article_content(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                paragraphs = soup.find_all(['p', 'div'], class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['content', 'article', 'body', 'text']
                ))
                if not paragraphs:
                    paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs[:5]])
                return content[:1000]
        except Exception as e:
            logger.error(f"Məqalə məzmunu çəkmə xətası: {e}")
        return ""

    def fetch_cryptonews_news(self) -> List[NewsItem]:
        try:
            news_items = []
            source_config = NEWS_SOURCES['cryptonews']
            feed = feedparser.parse(source_config['rss_url'])
            for entry in feed.entries[:10]:
                try:
                    title = entry.title
                    url = entry.link
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    published = datetime(*entry.published_parsed[:6])
                    if published > datetime.now() - timedelta(days=1):
                        content = self._fetch_article_content(url)
                        news_item = NewsItem(
                            title=title,
                            content=content,
                            url=url,
                            source=source_config['name'],
                            published_date=published,
                            summary=summary
                        )
                        if not self._is_news_seen(news_item):
                            news_items.append(news_item)
                            self._mark_news_as_seen(news_item)
                except Exception as e:
                    logger.error(f"Crypto News xəbər emal xətası: {e}")
            return news_items
        except Exception as e:
            logger.error(f"Crypto News RSS xətası: {e}")
            return []

    def fetch_newsbtc_news(self) -> List[NewsItem]:
        try:
            news_items = []
            source_config = NEWS_SOURCES['newsbtc']
            feed = feedparser.parse(source_config['rss_url'])
            for entry in feed.entries[:10]:
                try:
                    title = entry.title
                    url = entry.link
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    published = datetime(*entry.published_parsed[:6])
                    if published > datetime.now() - timedelta(days=1):
                        content = self._fetch_article_content(url)
                        news_item = NewsItem(
                            title=title,
                            content=content,
                            url=url,
                            source=source_config['name'],
                            published_date=published,
                            summary=summary
                        )
                        if not self._is_news_seen(news_item):
                            news_items.append(news_item)
                            self._mark_news_as_seen(news_item)
                except Exception as e:
                    logger.error(f"NewsBTC xəbər emal xətası: {e}")
            return news_items
        except Exception as e:
            logger.error(f"NewsBTC RSS xətası: {e}")
            return []

    def fetch_all_news(self) -> List[NewsItem]:
        all_news = []
        try:
            results = [
                self.fetch_coindesk_news(),
                self.fetch_theblock_news(),
                self.fetch_cointelegraph_news(),
                self.fetch_cryptonews_news(),
                self.fetch_newsbtc_news()
            ]
            for result in results:
                if isinstance(result, list):
                    all_news.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Xəbər çəkmə xətası: {result}")
            all_news.sort(key=lambda x: x.published_date, reverse=True)
            logger.info(f"Cəmi {len(all_news)} yeni xəbər tapıldı")
            return all_news
        except Exception as e:
            logger.error(f"Ümumi xəbər çəkmə xətası: {e}")
            return []

    def cleanup_seen_news(self, hours: int = 24):
        """Köhnə xəbərləri təmizləyir"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        try:
            # Fayl məlumatlarını yenidən yükləyir və köhnələri silir
            if os.path.exists(self.seen_news_file):
                with open(self.seen_news_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Yalnız son saatlar ərzindəki xəbərləri saxlayır
                filtered_data = []
                for item in data:
                    saved_at = datetime.fromisoformat(item['saved_at'])
                    if saved_at > cutoff_time:
                        filtered_data.append(item)
                
                # Yenilənmiş məlumatları saxlayır
                with open(self.seen_news_file, 'w', encoding='utf-8') as f:
                    json.dump(filtered_data, f, ensure_ascii=False, indent=2)
                
                # Memory-dəki seti də yeniləyir
                self.seen_news = {item['hash'] for item in filtered_data}
                logger.info(f"Temizlik: {len(filtered_data)} xəbər saxlandı, köhnələr silindi")
        except Exception as e:
            logger.error(f"Temizlik xətası: {e}")
    
    def get_seen_news_stats(self) -> Dict:
        """Görülən xəbərlər haqqında statistika qaytarır"""
        try:
            stats = {
                'total_seen': len(self.seen_news),
                'recent_news': []
            }
            
            if os.path.exists(self.seen_news_file):
                with open(self.seen_news_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stats['file_entries'] = len(data)
                    
                    # Son 5 xəbəri göstər
                    recent = sorted(data, key=lambda x: x.get('saved_at', ''), reverse=True)[:5]
                    for item in recent:
                        stats['recent_news'].append({
                            'title': item.get('title', 'N/A')[:50] + '...',
                            'source': item.get('source', 'N/A'),
                            'saved_at': item.get('saved_at', 'N/A')
                        })
            
            return stats
        except Exception as e:
            logger.error(f"Statistika alınma xətası: {e}")
            return {'total_seen': len(self.seen_news), 'error': str(e)} 