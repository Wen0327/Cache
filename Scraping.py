import os
import requests
from bs4 import BeautifulSoup

# 設定圖片下載的目標資料夾

# downloaded_Char downloaded_Ball
download_folder = os.path.expanduser("~/Downloads/Side Project/Cache/downloaded_Char")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# 從6199開始到6551的範圍，逐個下載
start_number = 6199
end_number = 6551

# 儲存檔名從1.png開始
image_number = 1

# 遍歷範圍，下載圖片
for random_number in range(start_number, end_number + 1):
    url = f"https://dic.xflag.com/monsterstrike/assets-update/img/monster/{random_number}/character.webp"
    # switch to character
    # f"https://dic.xflag.com/monsterstrike/assets-update/img/monster/{random_number}/character.webp"
    # switch to ball
    # f"https://dic.xflag.com/monsterstrike/assets-update/img/monster/{random_number}/ball.webp"

    # 檢查圖片是否已經存在
    img_name = f"{image_number}.png"
    img_path = os.path.join(download_folder, img_name)
    if os.path.exists(img_path):
        print(f"圖片已存在，跳過: {img_name}")
        image_number += 1  # 檔名遞增
        continue

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
