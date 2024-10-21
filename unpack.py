import zipfile
import os
import glob
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import plistlib
import base64


def extract_ipa(ipa_path, extract_to):
    # 確認目標資料夾是否存在，若不存在則建立
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # 嘗試打開並解壓 ipa 文件
    try:
        with zipfile.ZipFile(ipa_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extracted {ipa_path} to {extract_to}")
    except zipfile.BadZipFile:
        print("Error: The provided file is not a valid .zip/.ipa file.")
        return


def decode_base64_data(data, output_path):
    try:
        decoded_data = base64.b64decode(data)
        with open(output_path, "wb") as file:
            file.write(decoded_data)
        print(f"Saved decoded file: {output_path}")
    except Exception as e:
        print(f"Error decoding Base64 data: {e}")


def find_and_decode_plist(extract_directory):
    # 搜索解壓後的所有 .plist 文件
    plist_files = glob.glob(f"{extract_directory}/Payload/**/*.plist", recursive=True)

    if not plist_files:
        print("No .plist files found in the extracted .ipa.")
        return

    # 遍歷並解析所有 .plist 文件
    for plist_file in plist_files:
        try:
            with open(plist_file, "rb") as file:
                plist_data = plistlib.load(file)
            print(f"Parsed plist: {plist_file}")

            # 檢查 plist 中是否有 Base64 編碼的資料
            if isinstance(plist_data, dict):
                for key, value in plist_data.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, str):
                                # 檢查是否為 Base64 編碼的資料
                                try:
                                    output_filename = sub_key.replace("/", "_")
                                    output_path = os.path.join(
                                        extract_directory, output_filename
                                    )
                                    decode_base64_data(sub_value, output_path)
                                except Exception as e:
                                    print(f"Error processing {sub_key}: {e}")
        except Exception as e:
            print(f"Error reading plist file {plist_file}: {e}")


def main():
    # 使用 tkinter 開啟文件選擇對話框
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗
    ipa_file_path = filedialog.askopenfilename(
        title="Select .ipa File",
        filetypes=[("IPA files", "*.ipa")],
    )

    # 如果用戶沒有選擇文件，則退出
    if not ipa_file_path:
        print("No file selected.")
        return

    extract_directory = "./extracted_app"

    # 解壓 ipa 文件
    extract_ipa(ipa_file_path, extract_directory)

    # 查找並解碼 Base64 編碼的 .plist 文件
    find_and_decode_plist(extract_directory)


if __name__ == "__main__":
    main()
