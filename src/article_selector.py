import google.generativeai as genai
import json
import os

class ArticleSelector:
    def __init__(self):
        # GitHub SecretsからAPIキーを取得
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
    
    def select_best_article(self, articles):
        """日本の個人投資家に最も価値のある記事を選定"""
        
        if not articles:
            print("No articles to select from.")
            return None
            
        # 記事リストを整形
        articles_text = "\n\n".join([
            f"{i+1}. 【{a['source']}】{a['title']}\n   概要: {a['summary'][:200]}"
            for i, a in enumerate(articles)
        ])
        
        prompt = f"""
あなたは日本の個人投資家向けメディアの編集者です。
以下の記事リストから、最も価値のある1本を選定してください。

【選定基準】
1. 日本の個人投資家の関心が高いテーマ（米国株、配当、成長戦略等）
2. 具体的な投資の示唆がある内容
3. 時事性があり、今週中に読む価値がある
4. 翻訳・解説した際に学びがある内容

【記事リスト】
{articles_text}

【出力形式】
選定した記事の番号（1-{len(articles)}）のみを数字で返してください。
理由は不要です。
"""
        
        try:
            # セーフティ設定を緩和（投資ニュースでブロックされないようにする）
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            response = self.model.generate_content(prompt, safety_settings=safety_settings)
            
            # rate limit対策の待機時間
            import time
            time.sleep(2)
            
            selected_num = int(response.text.strip()) - 1
            if selected_num < 0 or selected_num >= len(articles):
                selected_num = 0
        except Exception as e:
            print(f"Failed to parse AI response or hit API error: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"API Error Details: {e.response.text}")
            elif hasattr(response, 'prompt_feedback'):
                print(f"Prompt Feedback: {response.prompt_feedback}")
            selected_num = 0
        
        return articles[selected_num]
    
    def save_selection(self, article, filename='_drafts/selected.json'):
        if not article: return
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        return filename

# テスト用
if __name__ == '__main__':
    # 候補記事を読み込み
    try:
        with open('_drafts/candidates.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        selector = ArticleSelector()
        best = selector.select_best_article(articles)
        if best:
            selector.save_selection(best)
            print(f"選定: {best['title']}")
    except FileNotFoundError:
        print("_drafts/candidates.json not found. Run rss_fetcher.py first.")
