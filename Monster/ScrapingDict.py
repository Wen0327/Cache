import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor

# 設定角色和球的基礎資料夾
char_folder = os.path.expanduser(
    "~/Downloads/Side Project/Cache/Downloads/downloaded_Char"
)
ball_folder = os.path.expanduser(
    "~/Downloads/Side Project/Cache/Downloads/downloaded_Ball"
)

# 如果資料夾不存在，則建立資料夾
os.makedirs(char_folder, exist_ok=True)
os.makedirs(ball_folder, exist_ok=True)

# 下載圖片的範圍
start_number = 1
end_number = 7000


# 定義下載並儲存圖片的函式
def download_image(url, folder, filename):
    file_path = os.path.join(folder, filename)

    # 檢查圖片是否已經存在
    if os.path.exists(file_path):
        print(f"圖片已存在，跳過: {filename}")
        return

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(file_path, "wb") as handler:
                handler.write(response.content)
            print(f"圖片已下載: {filename}")
        else:
            print(f"圖片不存在，跳過: {filename}")
    except requests.RequestException as e:
        print(f"下載失敗，跳過: {filename}，錯誤訊息: {e}")


# 定義主要下載邏輯
def download_images_for_number(number):
    # 角色和球的 URL
    char_url = f"https://dic.xflag.com/monsterstrike/assets-update/img/monster/{number}/character.webp"
    ball_url = f"https://dic.xflag.com/monsterstrike/assets-update/img/monster/{number}/ball.webp"

    # 角色和球的檔名
    char_filename = f"{number}.png"
    ball_filename = f"{number}.png"

    # 下載角色和球的圖片
    download_image(char_url, char_folder, char_filename)
    download_image(ball_url, ball_folder, ball_filename)


start_time = time.time()
# 使用多執行緒來並行下載圖片 根據網路和電腦性能來調整max_workers
with ThreadPoolExecutor(max_workers=25) as executor:
    executor.map(download_images_for_number, range(start_number, end_number + 1))

end_time = time.time()
elapsed_time = end_time - start_time

print(f"圖片下載完成。 耗時: {elapsed_time:.2f} 秒")
