import os
import tkinter as tk
from tkinter import ttk, messagebox
from io import BytesIO
from PIL import Image, ImageTk
import json
import re
import requests


class ImageSelectorApp:
    def __init__(self, root, data):
        self.root = root
        self.data = data
        self.root.title("图片选择器")
        self.root.geometry("800x600")

        self.unloaded_images = []  # 未加载的图片列表

        # 输入框
        self.label = tk.Label(root, text="输入搜索关键字：")
        self.label.pack(pady=10)
        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=10)

        # 搜索按钮
        self.search_button = tk.Button(
            root, text="搜索图片", command=self.search_images
        )
        self.search_button.pack(pady=10)

        # 创建一个带滚动条的画布
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(
            root, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定滚动事件
        self.canvas.bind("<Configure>", self.check_visible_images)
        self.canvas.bind_all("<MouseWheel>", self.check_visible_images)

    def search_images(self):
        keyword = self.entry.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键字")
            return

        # 清空图片区域和未加载队列
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.unloaded_images.clear()

        # 执行模糊搜索
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        matches = [item for item in self.data["urls"] if pattern.search(item["alt"])]

        if not matches:
            messagebox.showinfo("提示", "未找到匹配的图片")
            return

        # 将匹配的图片加入未加载队列
        for index, item in enumerate(matches):
            frame = ttk.Frame(
                self.scrollable_frame, borderwidth=1, relief="solid", padding=5
            )
            frame.grid(row=index // 3, column=index % 3, padx=5, pady=5)
            label = tk.Label(frame, text="加载中...", wraplength=150, justify="center")
            label.pack()
            self.unloaded_images.append((frame, item["url"], item["alt"]))

        self.check_visible_images()

    def check_visible_images(self, event=None):
        """
        检查可视区域内的未加载图片并加载它们
        """
        visible_top = self.canvas.canvasy(0)
        visible_bottom = visible_top + self.canvas.winfo_height()

        # 加载在可视范围内的图片
        for frame, url, alt in list(
            self.unloaded_images
        ):  # 使用 list 避免迭代时修改列表
            frame_top = frame.winfo_y()
            frame_bottom = frame_top + frame.winfo_height()
            if (
                visible_top <= frame_top <= visible_bottom
                or visible_top <= frame_bottom <= visible_bottom
            ):
                self.load_image(frame, url, alt)
                self.unloaded_images.remove((frame, url, alt))

    def load_image(self, frame, url, alt):
        """
        加载图片并显示在指定的 frame 中
        """
        try:
            # 下载图片
            img_data = BytesIO(requests.get(url).content)
            img = Image.open(img_data)
            img = img.resize((150, 150))  # 调整大小为 150x150
            img_tk = ImageTk.PhotoImage(img)

            # 清空 frame 并添加图片和描述
            for widget in frame.winfo_children():
                widget.destroy()
            img_label = tk.Label(frame, image=img_tk)
            img_label.image = img_tk
            img_label.pack()

            alt_label = tk.Label(frame, text=alt, wraplength=150, justify="center")
            alt_label.pack()

        except Exception as e:
            print(f"无法加载图片: {e}")


if __name__ == "__main__":
    # 自动获取 JSON 文件的路径
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 当前脚本所在目录
    json_path = os.path.join(base_dir, "gogo.json")  # 构建 JSON 文件路径

    try:
        # 加载 JSON 数据
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # 启动 Tkinter 应用程序
        root = tk.Tk()
        app = ImageSelectorApp(root, data)
        root.mainloop()

    except FileNotFoundError:
        print(f"找不到文件: {json_path}")
    except json.JSONDecodeError as e:
        print(f"JSON 文件解析失败: {e}")
