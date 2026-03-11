# Global Invest Bot

AIを活用して毎朝最新の投資ニュース（海外）を取得・選定・翻訳要約し、note用の下書きを自動生成する半自動化システムです。

## 技術スタック
- GitHub Actions (Cron実行)
- Python 3.10
- feedparser (RSS取得)
- Google Gemini API (記事選定・翻訳・要約)

## セットアップ手順
1. 本リポジトリをForkまたはClone
2. `Settings` > `Secrets and variables` > `Actions` に `GEMINI_API_KEY` を設定
3. GitHub Actionsで `workflow_dispatch` を使って手動テスト実行

## ディレクトリ構成
- `src/rss_fetcher.py` : RSSからニュースを取得し、`_drafts/candidates.json` に保存
- `src/article_selector.py` : 取得したニュースからAIが1記事を選定し、`_drafts/selected.json` に保存
- `src/translator.py` : 選定された記事をAIが翻訳・要約し、`_drafts/draft_*.md` を生成
- `.github/workflows/daily-news.yml` : 毎朝6:00(JST)に上記スクリプトを自動化
