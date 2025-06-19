import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
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
        self.hash = hash(f"{title}{url}")

    def __eq__(self, other):
        return isinstance(other, NewsItem) and self.hash == other.hash

    def __hash__(self):
        return self.hash

class NewsFetcher:
    def __init__(self):
        self.seen_news = set()

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
                        if news_item not in self.seen_news:
                            news_items.append(news_item)
                            self.seen_news.add(news_item)
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
                        if news_item not in self.seen_news:
                            news_items.append(news_item)
                            self.seen_news.add(news_item)
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
                        if news_item not in self.seen_news:
                            news_items.append(news_item)
                            self.seen_news.add(news_item)
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

    def fetch_all_news(self) -> List[NewsItem]:
        all_news = []
        try:
            results = [
                self.fetch_coindesk_news(),
                self.fetch_theblock_news(),
                self.fetch_cointelegraph_news()
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
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.seen_news = {
            news for news in self.seen_news 
            if news.published_date > cutoff_time
        } 