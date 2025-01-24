import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def initialize_webdriver(headless=True):
    """初始化 Selenium WebDriver。"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=chrome_options)


def save_image(img_url, save_dir, index, base_url):
    """
    儲存圖片，處理普通 URL
    """

    if img_url.startswith("data:image"):
        print("Base64 圖片跳過")
        return

    if not img_url.startswith("http"):
        img_url = requests.compat.urljoin(base_url, img_url)

    img_name = os.path.basename(img_url.split("?")[0])
    file_path = os.path.join(save_dir, img_name)

    # check whether the image been download
    if os.path.exists(file_path):
        print(f"圖片已存在，跳過: {file_path}")
        return

    try:
        response = requests.get(img_url, stream=True, timeout=10)
        response.raise_for_status()
        if "image" in response.headers.get("Content-Type", ""):
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"圖片下載成功: {file_path}")
        else:
            print(f"非圖片資源: {img_url}")
    except requests.RequestException as e:
        print(f"下載失敗: {img_url}, 錯誤: {e}")


def fetch_page_source(driver, url, wait_time=5):
    """使用 Selenium 獲取網頁源代碼，沿用同一個 WebDriver 實例。"""
    driver.get(url)
    time.sleep(wait_time)  # 等待 JavaScript 加載完成
    return driver.page_source


def parse_images(soup, css_class):
    """
    從 HTML 中提取 <img> 標籤的圖片 URL。
    """
    img_tags = soup.find_all("img", class_=lambda cls: cls and css_class in cls)
    return [(img.get("src"), idx) for idx, img in enumerate(img_tags) if img.get("src")]


def parse_background_images(soup):
    """
    從 HTML 中提取背景圖片的 URL。
    """
    div_tags = soup.find_all("div", style=True)
    images = []
    for index, div in enumerate(div_tags):
        style = div.get("style", "")
        if "background-image" in style:
            start = style.find("url(") + 4
            end = style.find(")", start)
            img_url = style[start:end].strip("\"'")
            images.append((img_url, index))
    return images


def download_images(image_list, save_dir, base_url):
    """
    使用多執行緒下載圖片。
    """
    os.makedirs(save_dir, exist_ok=True)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for img_url, index in image_list:
            executor.submit(save_image, img_url, save_dir, index, base_url)


def download_avatar_images(driver, base_url, save_dir="downloaded_images/avatar"):
    """
    下載 class 包含 "avatar" 的圖片。
    """
    url = base_url.format(worldIndex=1)
    html = fetch_page_source(driver, url)
    soup = BeautifulSoup(html, "html.parser")
    avatar_images = parse_images(soup, css_class="avatar")
    print(f"找到 {len(avatar_images)} 張 avatar 圖片，開始下載...")
    download_images(avatar_images, save_dir, base_url)


def download_world_images(driver, base_url, save_dir="downloaded_images", max_world=10):
    """
    循環下載不同 worldIndex 的背景圖片。
    """
    previous_images = set()
    for world_index in range(1, max_world + 1):
        world_save_dir = os.path.join(save_dir, f"world{world_index}")
        os.makedirs(world_save_dir, exist_ok=True)

        url = base_url.format(worldIndex=world_index)
        html = fetch_page_source(driver, url)
        soup = BeautifulSoup(html, "html.parser")

        background_images = parse_background_images(soup)
        if not background_images:
            print(f"worldIndex {world_index} 找不到背景圖片，結束處理。")
            break

        current_images_set = set(img[0] for img in background_images)
        if current_images_set == previous_images:
            print("下載的圖片與上一個 worldIndex 相同，跳過處理。")
            continue

        print(f"worldIndex {world_index}: 開始下載背景圖片...")
        download_images(background_images, world_save_dir, url)
        previous_images = current_images_set


if __name__ == "__main__":
    base_url = (
        "https://hsr.hoyoverse.com/zh-tw/character?worldIndex={worldIndex}&charIndex=1"
    )

    driver = initialize_webdriver()  # 初始化 WebDriver

    try:
        download_avatar_images(driver, base_url)
        download_world_images(driver, base_url)
    finally:
        driver.quit()  # 程式執行結束後關閉 WebDriver
