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
            print(f"Base64 跳過")
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


def download_avatar_images(base_url, save_dir="downloaded_images/avatar"):
    """
    下載一次所有 class 包含 "avatar" 的 <img> 圖片，並保存到 avatar 資料夾。
    """
    os.makedirs(save_dir, exist_ok=True)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無界面模式
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        url = base_url.format(worldIndex=1)
        driver.get(url)
        print(f"等待 JavaScript 加载完成...")
        time.sleep(5)  # 等待 JavaScript 加载完成

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        avatar_images = []
        img_tags = soup.find_all(
            "img", class_=lambda cls: cls and ("avatar" in cls or "char-pro" in cls)
        )
        for index, img_tag in enumerate(img_tags):
            img_url = img_tag.get("src")
            if img_url:
                avatar_images.append((img_url, index))

        print(f"找到 {len(avatar_images)} 張 avatar 圖片，開始下載...")

        # 使用 ThreadPoolExecutor 進行多執行緒下載
        with ThreadPoolExecutor(max_workers=10) as executor:
            for img_url, index in avatar_images:
                executor.submit(save_image, img_url, save_dir, index, url)

    finally:
        driver.quit()


def download_images_with_selenium(url, save_dir="downloaded_images"):
    """
    使用 Selenium 從動態網頁下載所有 style="background-image: url()" 的圖片。

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

        # 找到所有背景圖片
        div_tags = soup.find_all("div", style=True)
        background_images = []
        for index, div_tag in enumerate(div_tags):
            style = div_tag.get("style", "")
            if "background-image" in style:
                start_idx = style.find("url(") + 4
                end_idx = style.find(")", start_idx)
                img_url = style[start_idx:end_idx].strip("\"'")
                if img_url:
                    background_images.append((img_url, index))

        print(f"找到 {len(background_images)} 張背景圖片，開始下載...")

        # 使用 ThreadPoolExecutor 進行多執行緒下載
        with ThreadPoolExecutor(max_workers=10) as executor:
            for img_url, index in background_images:
                executor.submit(save_image, img_url, save_dir, index, url)

        return background_images

    finally:
        driver.quit()


if __name__ == "__main__":
    base_url = (
        "https://hsr.hoyoverse.com/zh-tw/character?worldIndex={worldIndex}&charIndex=1"
    )
    save_dir = "downloaded_images"

    # 首次下載 avatar 圖片
    download_avatar_images(base_url)

    worldIndex = 1
    previous_images = set()

    while True:
        world_save_dir = os.path.join(save_dir, f"world{worldIndex}")
        os.makedirs(world_save_dir, exist_ok=True)

        url = base_url.format(worldIndex=worldIndex)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get(url)
            time.sleep(3)  # 等待頁面加載完成
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # 檢查頁面是否有效
            div_tags = soup.find_all("div", style=True)
            valid_images = any(
                "background-image" in div.get("style", "") for div in div_tags
            )
            if not valid_images:
                print(f"worldIndex {worldIndex} 找不到背景圖片，結束處理。")
                break

            print(f"處理 URL: {url}")
            current_images = download_images_with_selenium(url, world_save_dir)

            # 檢查圖片是否與上一個 worldIndex 相同
            current_images_set = set([img[0] for img in current_images])
            if current_images_set == previous_images:
                print("下載的圖片與上一個 worldIndex 相同，跳到下一個 worldIndex。")
                break

            previous_images = current_images_set

        except Exception as e:
            print(f"處理失敗: {url}, 錯誤: {e}")
            break

        finally:
            driver.quit()

        # worldIndex + 1
        worldIndex += 1

        # 測試到某個 worldIndex 停止
        if worldIndex > 10:  # 可調整最大 worldIndex 上限
            print("結束所有處理。")
            break
