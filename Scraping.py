import os
import requests
from bs4 import BeautifulSoup

# 設定圖片下載的目標資料夾
download_folder = os.path.expanduser("~/Downloads/Side Project/Cache/downloaded_images")
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# 目標網址
url = (
    "https://dic.xflag.com/monsterstrike/assets-update/img/monster/6546/character.webp"
)

# 下載圖片
img_data = requests.get(url).content

# 儲存圖片
img_name = "character.webp"
img_path = os.path.join(download_folder, img_name)
with open(img_path, "wb") as handler:
    handler.write(img_data)

print(f"圖片已下載到: {img_path}")
