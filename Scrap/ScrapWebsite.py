import requests
import os
from PIL import Image
from io import BytesIO


def download_images(url):
    # 取得圖片的檔案名稱
    image_name = url.split("/")[-1]
    # 檢查目錄是否存在，如果不存在則創建
    if not os.path.exists("images"):
        os.makedirs("images")
    # 設定儲存路徑
    save_path = os.path.join("images", image_name)

    # 發送請求取得圖片內容
    response = requests.get(url)

    # 檢查請求是否成功
    if response.status_code == 200:
        # 以二進位寫入圖片檔案
        with open(save_path, "wb") as file:
            file.write(response.content)
        print(f"圖片已儲存到 {save_path}")

        # 嘗試用 PIL 開啟圖片來確認是否為有效圖片
        try:
            img = Image.open(BytesIO(response.content))
            img.verify()  # 驗證圖片
            print("圖片下載並驗證成功！")
        except Exception as e:
            print("圖片可能損壞或格式不支援:", e)
    else:
        print(f"下載圖片失敗，狀態碼：{response.status_code}")


# 測試用圖片網址
image_url = "https://www.monster-strike.com/entryimage/FbMXdUzC20241017.png"
download_images(image_url)
