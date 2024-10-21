import os
import requests
from bs4 import BeautifulSoup

# 設定圖片下載的目標資料夾
# switch to character
# downloaded_Char

# switch to ball
# downloaded_Ball

# switch to ranking
# downloaded_Ranking

# need to change the path
download_folder = os.path.expanduser(
    "~/Downloads/Side Project/Cache/downloaded_Ranking"
)
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# 從6199開始到6551的範圍，逐個下載
start_number = 1
end_number = 100

# 遍歷範圍，下載圖片
for random_number in range(start_number, end_number + 1):
    url = f"https://www.monster-strike.com/entryimage/B3F19HUBxeQi_{random_number}.png"

    # switch to character
    # f"https://dic.xflag.com/monsterstrike/assets-update/img/monster/{random_number}/character.webp"

    # switch to ball
    # f"https://dic.xflag.com/monsterstrike/assets-update/img/monster/{random_number}/ball.webp"

    # switch to ranking
    # f"https://www.monster-strike.com/entryimage/B3F19HUBxeQi_1.png

    # 儲存檔名與number相同
    # 檢查圖片是否已經存在
    img_name = f"{random_number}.png"
    img_path = os.path.join(download_folder, img_name)
    if os.path.exists(img_path):
        print(f"圖片已存在，跳過: {img_name}")
        continue

    try:
        # 下載圖片
        response = requests.get(url, timeout=10)
        # 檢查是否為成功的響應（狀態碼200）
        if response.status_code == 200:
            img_data = response.content

            # 儲存圖片，檔名依次從5.png開始
            img_name = f"{random_number}.png"
            img_path = os.path.join(download_folder, img_name)
            with open(img_path, "wb") as handler:
                handler.write(img_data)

            print(f"圖片已下載: {img_name}")

        else:
            print(f"圖片不存在，跳過: {random_number}")

    except requests.RequestException as e:
        print(f"下載失敗，跳過: {random_number}，錯誤訊息: {e}")

print("圖片下載完成。")
