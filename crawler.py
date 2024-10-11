import json
import random
import sys
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 接收命令行參數（Google Maps URL），保留基本驗證
if len(sys.argv) < 2:  # 檢查命令行中傳入的參數數量是否小於 2，小於2代表除了腳本名稱之外，使用者並沒有提供任何參數（例如 Google Maps URL）
    sys.exit(1)  # 程式異常退出（這裡表示缺少必需的參數）

landmark_url = sys.argv[1]  # 傳入Google Maps URL

# Webdriver 設定
options = Options()
options.add_argument('--headless') #啟動無頭模式
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
options.add_argument('--log-level=3') #不輸出log
options.add_argument('--disable-gpu') #windows必須加入此行
options.add_experimental_option('excludeSwitches', ['enable-logging']) #不輸出logging
webdriver_path = 'WEBDRIVER_PATH'  # 你的webdriver路徑
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service, options=options)
driver.get(landmark_url)

sleep(random.uniform(1, 3))

#點選「評論」的按鈕
button = driver.find_elements(By.CSS_SELECTOR, 'button.hh2c6')[1]
button.click()

sleep(0.1)

#點選「排序」按鈕
button_sort = driver.find_elements(By.CSS_SELECTOR, 'button.g88MCb.S9kvJb')[2]
button_sort.click()

sleep(0.1)

#點選「最新」按鈕
button_new = driver.find_element(By.CSS_SELECTOR, "div[data-index='1']")
button_new.click()

sleep(random.uniform(1, 3))

# 找到可以捲動的評論區域
scrollable_div = driver.find_element(By.CSS_SELECTOR, '.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde')

# 記錄初始的高度
previous_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

while True:

    # 捲動評論區域到底部
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)

    try:
        # 等待評論區域的高度增加，最多等待20秒
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return arguments[0].scrollHeight", scrollable_div) > previous_height
        )
    except TimeoutException:
        print("所有評論已開啟完畢")
        break

    # 更新高度
    previous_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

def click_all_buttons(selectors):
    # 使用 WebDriverWait 等待任一按鈕出現
    try:
        for selector in selectors:
            buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
            # 點擊所有找到的按鈕
            for button in buttons:
                button.click()
    except TimeoutException:
        print("沒有找到按鈕，跳過此步驟。")
    except Exception as e:
        print(f"發生其他錯誤：{e}")

# 定義要點擊的按鈕 CSS 選擇器，前者為原文按鈕，後者為全文按鈕
selectors = ['button.kyuRq.fontTitleSmall.WOKzJe', 'button.w8nwRe.kyuRq']

# 等待並點擊頁面上任一符合的按鈕
click_all_buttons(selectors)

#將資料存儲為 JSON 格式
reviews = []

# 找到所有確實包含評分的評論父級元素
review_containers = driver.find_elements(By.CSS_SELECTOR, 'div.GHT2ce:has(span[role="img"][aria-label*="顆星"])')
for idx, container in enumerate(review_containers):
    # 獲取評分
    stars_text = container.find_element(By.CSS_SELECTOR, 'span[role="img"][aria-label*="顆星"]').get_attribute("aria-label")
    # 嘗試獲取評論內容
    try:
        review_text = container.find_element(By.CSS_SELECTOR, 'span.wiI7pd').text
    except:
        review_text = ""
    # 將評論資訊儲存為字典格式
    review_data = {
        "評論編號": idx + 1,
        "評分": stars_text,
        "內容": review_text
    }
    
    reviews.append(review_data)

# 將所有評論資訊寫入 JSON 檔案
with open('Google_Maps_reviews.json', 'w', encoding='utf-8') as file:
    json.dump(reviews, file, ensure_ascii=False, indent=4)

print("評論資料已成功寫入 'Google_Maps_reviews.json' 檔案")

driver.close()