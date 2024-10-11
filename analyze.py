import json
import os
import uuid  # 用於生成隨機 session_id

import openai

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 載入 .env 檔案
load_dotenv()

# 設定 OpenAI API 金鑰
openai.api_key = os.getenv('OPENAI_API_KEY')

# 初始化 ChatOpenAI 模型
llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18", api_key=openai.api_key)

# 聊天會話管理功能，可以管理多個對話
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
	if session_id not in store:
		store[session_id] = ChatMessageHistory()
	return store[session_id]

# 建立會話鏈，並加入記憶模組
conversation = RunnableWithMessageHistory(
    runnable=llm,
    get_session_history=get_session_history,
    max_history=10  # 每個會話最多保留多少條歷史記錄
)

# 生成隨機的 session_id
session_id = str(uuid.uuid4())

# 分析評論的功能
def analyze_reviews():
    try:    
        
        # 讀取評論資料
        with open('Google_Maps_reviews.json', 'r', encoding='utf-8') as f:
            reviews = json.load(f)

        # 取得評論編號、評分和內容，只輸出文字
        extracted_reviews = []
        for review in reviews:
            review_text = f"{review['評論編號']}, {review['評分']}, {review['內容']}"
            extracted_reviews.append(review_text)

        # 將提取的評論轉換為單個文本區塊
        reviews_text = "\n".join(extracted_reviews)

        # 提供 prompt，進行彙整
        user_prompt = f"""
        - 請你秉持著公正客觀的精神，根據評論者表述的具體內容，不加入額外的情感或評價，彙整所有評論
        - 你必須考量到不同面向（譬如正面、負面以及中立的評論）進行彙整，如發現評論包含多重情緒面向，請確保每個面向都被分別處理，最後得出一個綜合的結果（切勿列舉出個別評論）；當然，畢竟一個場域同時存在不同的因素，影響使用者（或消費者）對於該地的觀感，也因此一個留言中難免會同時包和正面及負面的評價

        - 評論者有時候會善於利用反諷的方式表達他的想法，也請你試著去識別這些隱含在表面下的真實意義；若發現反諷或隱含的意思，請基於上下文和語調進行合理推測，並標註此為推測性的分析
        - 這些評論者可能來自不同國家，因此可能包含了許多不同的語言；也因此，你需要克服不同語言的問題，有些部分可能會較為口語化，你必須瞭解這些口語用法的真實意義；假使遇到不確定的語言表達或翻譯困難時，請明確標注為翻譯模糊部分，而非自行填補內容
        - 有些評論者可能偏好加入 emoji，或是顏文字，也請你嘗試辨別出來它們所代表的意義；若 emoji 的意義存在歧義，請提供多種可能的解釋，並根據評論的上下文推測最可能的含義
        - 另外你的分析也需要考量到同一則評論的星星數，譬如有的客人可能只會留言：青醬義大利麵；這就會取決於他給的星星數，給一顆星跟給五顆星，代表著是對這個餐點有非常不同的評價；換句話說，如果缺乏評論文字、評論太過簡短或表述不明確，則以星星數作為輔助判斷該評論者的滿意度
        - 留言的時間點也反應了該地標的時間變化，因此近一步你可以考慮分析近期的狀況，和較為早期的狀況；請分析評論的時間分布，並嘗試識別該地標的評價是否隨時間呈現趨勢變化
        - 請根據我提供的資料進行分析，回覆必須嚴格基於提供的資訊。若資料不足以進行詳細分析或形成結論，請明確指出，而不是捏造假設或擴展的情境。我期望的是實事求是的回應，即便資料有限，也不應基於假設情境進行推斷；如發現評論數量不足以得出有意義的結論，請清楚說明分析限制

        - 請逐一檢視每則評論，並根據語境進行判斷，而非僅根據關鍵字進行機械式分類，接著才著手進行彙整
        - 請以繁體中文回覆
        - 除了數字標號的內容外，請勿回覆多餘的內容
        - 請幫我彙整出約1200字的回覆
        最後，請你幫我結果整理成幾個部分，並按照我提供的數字標號自行分段：
        1.正面評論
        2.負面評論
        3.中性評論
        4.綜合討論
        以下是所有的評論，每一行由左到右分別是評論編號、評分、內容：
        {reviews_text}
        """
        response = conversation.invoke(input=user_prompt, config={'configurable': {'session_id': session_id}})
    #    return response
    
        # 確保回應內容轉換為純文字
        response_text = response.content.replace("\n", "<br>")
        #response_text = str(response)
        return response_text
    
    except Exception as e:
        # 捕捉並輸出任何錯誤，方便除錯
        print(f"Error during review analysis: {str(e)}")
        return f"Error during review analysis: {str(e)}"

# 處理使用者提問的功能
def handle_user_question(question):
    try:
        response = conversation.invoke(input=question, config={'configurable': {'session_id': session_id}})
        # 確保回應內容轉換為純文字
        response_text = response.content.replace("\n", "<br>")
        return response_text
    except Exception as e:
        return f"Error during question handling: {str(e)}"