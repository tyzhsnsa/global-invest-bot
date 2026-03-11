import feedparser
import json
import os

class RSSFetcher:
    def __init__(self):
        self.feeds = {
            'seeking_alpha': 'http://seekingalpha.com/feed.xml',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'yahoo_finance': 'https://finance.yahoo.com/rss/'
        }
    
    def fetch_latest(self, max_articles=10):
        """最新記事を取得"""
        all_articles = []
        
        for source, url in self.feeds.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:  # 各ソースから5件
                    article = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', '')[:500],
                        'published': entry.get('published', ''),
                        'source': source
                    }
                    all_articles.append(article)
            except Exception as e:
                print(f"Error fetching {source}: {e}")
        
        # 日付でソート（新しい順）
        all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        return all_articles[:max_articles]
    
    def save_to_json(self, articles, filename='_drafts/candidates.json'):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        return filename

# テスト用
if __name__ == '__main__':
    fetcher = RSSFetcher()
    articles = fetcher.fetch_latest()
    fetcher.save_to_json(articles)
    print(f"{len(articles)}件の記事を取得しました")
