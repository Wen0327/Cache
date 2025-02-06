import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import time
import pytesseract
import cv2
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import asyncio

# 設定 Discord Bot
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# 創建 Bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 存儲查詢的包裹（使用 JSON 檔案）
PACKAGE_FILE = os.path.join(os.path.dirname(__file__), "pack.json")


def load_packages():
    if os.path.exists(PACKAGE_FILE):
        with open(PACKAGE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_packages(packages):
    with open(PACKAGE_FILE, "w") as f:
        json.dump(packages, f, indent=4)


# 設定包裹追蹤
@bot.command()
async def add(ctx, tracking_number: str):
    packages = load_packages()
    packages[str(ctx.author.id)] = tracking_number  # 直接覆蓋舊的單號
    save_packages(packages)
    await ctx.send(f"已設定您的查詢單號: {tracking_number}")


# 快速查詢已設定的包裹
@bot.command()
async def track(ctx):
    packages = load_packages()
    tracking_number = packages.get(str(ctx.author.id))

    if not tracking_number:
        await ctx.send("您尚未設定查詢單號，請使用 `!add 單號` 來設定。")
        return

    message = await ctx.send("查詢中: `[----------] 0%`")
    status = get_tracking_status(tracking_number)

    for i in range(1, 11):  # 模擬進度條 (10步)
        progress_bar = "█" * i + "-" * (10 - i)
        await message.edit(content=f"查詢中: `[{progress_bar}] {i * 10}%`")
        await asyncio.sleep(0.5)  # 模擬查詢時間

    # 真正執行查詢

    await message.edit(content=f"查詢結果: {status}")


# 手動輸入單號查詢
@bot.command()
async def check(ctx, tracking_number: str):
    message = await ctx.send("查詢中: `[----------] 0%`")

    for i in range(1, 11):  # 模擬進度條 (10步)
        progress_bar = "█" * i + "-" * (10 - i)
        await message.edit(content=f"查詢中: `[{progress_bar}] {i * 10}%`")
        await asyncio.sleep(0.5)  # 模擬查詢時間

    # 真正執行查詢
    status = get_tracking_status(tracking_number)
    await message.edit(content=f"查詢結果: {status}")


def get_tracking_status(tracking_number):

    # 設定 Selenium WebDriver

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://eservice.7-11.com.tw/e-tracking/search.aspx")
    time.sleep(2)

    tracking_input = driver.find_element(By.ID, "txtProductNum")
    tracking_input.send_keys(tracking_number)

    vcode_img = driver.find_element(By.ID, "ImgVCode")
    WebDriverWait(driver, 10).until(lambda d: vcode_img.get_attribute("src") != "")

    captcha_path = os.path.join(os.path.dirname(__file__), "captcha.png")
    vcode_img.screenshot(captcha_path)

    image = cv2.imread(captcha_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    processed = cv2.bitwise_not(cleaned)

    custom_config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"
    captcha_text = pytesseract.image_to_string(processed, config=custom_config).strip()

    vcode_input = driver.find_element(By.ID, "tbChkCode")
    vcode_input.send_keys(captcha_text)
    tracking_input.send_keys(Keys.RETURN)

    time.sleep(3)

    try:
        status_element = driver.find_element(By.ID, "timeline_status")
        status_text = status_element.text.strip()
    except Exception:
        status_text = "查詢失敗或查無資料"

    driver.quit()
    os.remove(captcha_path)

    return status_text


bot.run(DISCORD_TOKEN)
