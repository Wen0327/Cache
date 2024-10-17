import os
import requests
from bs4 import BeautifulSoup

# 設定圖片下載的目標資料夾
download_folder = os.path.expanduser("~/Downloads/Side Project/Cache/downloaded_images")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# 從6199開始到6547的範圍，逐個下載
start_number = 6199
end_number = 6547

# 儲存檔名從5.png開始
image_number = 5

# 遍歷範圍，下載圖片
for random_number in range(start_number, end_number + 1):
    url = f"https://dic.xflag.com/monsterstrike/assets-update/img/monster/{random_number}/character.webp"

    try:
        # 下載圖片
        response = requests.get(url, timeout=10)
        # 檢查是否為成功的響應（狀態碼200）
        if response.status_code == 200:
            img_data = response.content

            # 儲存圖片，檔名依次從5.png開始
            img_name = f"{image_number}.png"
            img_path = os.path.join(download_folder, img_name)
            with open(img_path, "wb") as handler:
                handler.write(img_data)

            print(f"圖片已下載: {img_name}")
            image_number += 1  # 檔名遞增
        else:
            print(f"圖片不存在，跳過: {random_number}")

    except requests.RequestException as e:
        print(f"下載失敗，跳過: {random_number}，錯誤訊息: {e}")

print("圖片下載完成。")
