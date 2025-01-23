import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor


def save_image(img_url, save_dir, index, url):
    """
    儲存圖片，包括處理普通 URL 和 Base64 圖片。

    :param img_url: 圖片 URL 或 Base64
    :param save_dir: 保存目錄
    :param index: 圖片索引
    :param url: 網頁的 URL
    """
    if img_url.startswith("data:image"):
        try:
            header, encoded = img_url.split(",", 1)
            file_ext = header.split("/")[1].split(";")[0]
            file_path = os.path.join(save_dir, f"data_image_{index}.{file_ext}")
            with open(file_path, "wb") as file:
                file.write(base64.b64decode(encoded))
            print(f"Base64 圖片保存成功: {file_path}")
        except Exception as e:
            print(f"無法保存 Base64 圖片: {e}")
    else:
        if not img_url.startswith("http"):
            img_url = requests.compat.urljoin(url, img_url)
        img_name = os.path.basename(img_url.split("?")[0])
        file_path = os.path.join(save_dir, img_name)
        try:
            img_response = requests.get(img_url, stream=True, timeout=10)
            img_response.raise_for_status()
            if "image" in img_response.headers.get("Content-Type", ""):
                with open(file_path, "wb") as file:
                    for chunk in img_response.iter_content(1024):
                        file.write(chunk)
                print(f"圖片下載成功: {file_path}")
            else:
                print(f"非圖片资源: {img_url}")
        except Exception as e:
            print(f"下載失敗: {img_url}, 错误: {e}")


def download_images_with_selenium(url, save_dir="downloaded_images"):
    """
    使用 Selenium從動態網頁下載所有 <img> 標籤的圖片，包括處理 data: URL 的圖片.

    :param url: 網頁的 URL
    :param save_dir: 圖片保存的目录
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無界面模式
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        print(f"等待 JavaScript 加载完成...")
        time.sleep(5)  # 等待 JavaScript 加载完成

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        img_tags = soup.find_all("img")
        os.makedirs(save_dir, exist_ok=True)
        print(f"找到 {len(img_tags)} 張圖片，開始下載...")

        # 使用 ThreadPoolExecutor 進行多執行緒下載
        with ThreadPoolExecutor(max_workers=10) as executor:
            for index, img_tag in enumerate(img_tags):
                img_url = (
                    img_tag.get("src")
                    or img_tag.get("data-src")
                    or img_tag.get("data-original")
                )
                if img_url:
                    executor.submit(save_image, img_url, save_dir, index, url)

    finally:
        driver.quit()


if __name__ == "__main__":
    target_url = input("請輸入網址: ")
    download_images_with_selenium(target_url)
