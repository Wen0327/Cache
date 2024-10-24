import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse


def download_images(url):
    # 發送 HTTP 請求獲取網頁內容
    response = requests.get(url)
    response.raise_for_status()  # 檢查請求是否成功

    # 解析網頁內容
    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")

    # 創建資料夾來保存圖片
    os.makedirs("downloaded_images", exist_ok=True)

    for img in img_tags:
        img_url = img.get("src")
        # 確保圖片 URL 完整
        img_url = urljoin(url, img_url)

        # 確認圖片的 URL 是否有效
        parsed_url = urlparse(img_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            continue

        # 獲取圖片的名稱
        img_name = os.path.basename(parsed_url.path)

        # 檢查檔案名稱是否已存在，若存在則自動修改名稱
        img_path = os.path.join("downloaded_images", img_name)
        base_name, extension = os.path.splitext(img_name)
        counter = 1
        while os.path.exists(img_path):
            img_name = f"{base_name}_{counter}{extension}"
            img_path = os.path.join("downloaded_images", img_name)
            counter += 1

        try:
            # 下載圖片
            img_data = requests.get(img_url).content
            with open(img_path, "wb") as img_file:
                img_file.write(img_data)
            print(f"Downloaded: {img_name}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")


# 使用範例
url = input("請輸入網址: ")
download_images(url)
