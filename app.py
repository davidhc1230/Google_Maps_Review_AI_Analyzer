import subprocess

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from analyze import store  # 導入 analyze.py 中的 物件

app = Flask(__name__)
CORS(app)  # 啟用 CORS，允許所有來源的跨域請求

# 首頁路由，返回 index.html
@app.route('/')
def index():
    return render_template('index.html')

# 爬取資料並執行分析
@app.route('/start-scraping', methods=['POST'])
def start_scraping():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"success": False, "error": "Invalid URL"})

    try:
        # 呼叫 crawler.py 爬蟲程式
        subprocess.run(['python', 'crawler.py', url], check=True)

        # 爬取完成後執行 analyze.py 進行評論分析
        from analyze import analyze_reviews
        result = analyze_reviews()

        # 將分析結果直接以 JSON 格式返回，而不是將用戶重定向到另一個頁面
        return jsonify({"success": True, "analysis": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 結果頁面路由
@app.route('/result')
def show_result():
    url = request.args.get('url')
    return render_template('result.html', url=url)

# 處理使用者提問
@app.route('/ask-question', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"success": False, "error": "Invalid question"})

    try:
        from analyze import handle_user_question
        answer = handle_user_question(question)
        return jsonify({"success": True, "answer": answer})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 處理重新分析請求的邏輯
@app.route('/clear-memory', methods=['POST'])
def clear_memory():
    try:
        store.clear()  # 清除所有儲存在 store 中的會話
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # 啟動 Flask 的開發伺服器，並設定伺服器的運行參數
