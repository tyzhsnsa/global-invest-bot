import google.generativeai as genai
import os
import json
from datetime import datetime

class ArticleTranslator:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
    
    def translate_and_summarize(self, article):
        """記事を翻訳し、note用フォーマットに整形"""
        
        prompt = f"""
以下の英語の投資記事を、日本の個人投資家向けに翻訳・解説してください。

【元記事タイトル】
{article.get('title', '')}

【元記事概要】
{article.get('summary', '')}

【出力形式】

【タイトル】
（日本語で魅力的なタイトル）

【海外投資家の注目ポイント】
・3つの重要ポイントを箇条書き

【日本の個人投資家への示唆】
・この戦略を日本市場で応用するには？
・注意すべきリスクは？

【元記事】
・URL: {article.get('link', '')}
・著者: （記載があれば）
・公開日: {article.get('published', '')}
"""
        
        try:
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            return response.text
        except Exception as e:
            print(f"Translation API error: {e}")
            if 'response' in locals() and hasattr(response, 'prompt_feedback'):
                print(f"Prompt Feedback (Blocked?): {response.prompt_feedback}")
            return "【タイトル】エラーにより取得できませんでした\n\nAPI制限またはセーフティフィルターによりブロックされました。ログを確認してください。"
    
    def create_note_draft(self, translated_content, article):
        """note用の完全な下書きを作成"""
        
        today = datetime.now().strftime('%Y-%m-%d')
        title = article.get('title', '無題')
        
        if '【タイトル】' in translated_content:
            try:
                parts = translated_content.split('【タイトル】')
                if len(parts) > 1:
                    title = parts[1].split('【')[0].strip()
            except Exception:
                pass
        
        draft = f"""# {title}

{translated_content}

---

※本記事は投資助言ではなく情報提供です。
※投資判断はご自身の責任で行ってください。
※過去のパフォーマンスは将来の成果を保証しません。

---
【自動生成された下書き】
生成日時: {today}
確認後、手動で投稿してください。
"""
        
        return draft
    
    def save_draft(self, draft, filename=None):
        if filename is None:
            today = datetime.now().strftime('%Y%m%d')
            filename = f'_drafts/draft_{today}.md'
            
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(draft)
        
        return filename

# テスト用
if __name__ == '__main__':
    try:
        with open('_drafts/selected.json', 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        translator = ArticleTranslator()
        translated = translator.translate_and_summarize(article)
        draft = translator.create_note_draft(translated, article)
        filename = translator.save_draft(draft)
        print(f"下書き保存: {filename}")
    except FileNotFoundError:
        print("_drafts/selected.json not found. Run article_selector.py first.")
