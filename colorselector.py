import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import random
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from PIL import Image, ImageTk
from matplotlib.colors import CSS4_COLORS, to_hex, to_rgb
import os

# 自定义配色保存路径
CUSTOM_PALETTE_FILE = "custom_palettes.json"

# 预设配色方案
PALETTES = {
    "高对比度": ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F', '#8491B4'],
    "柔和配色": sns.color_palette("pastel").as_hex(),
    "渐变色彩": [to_hex(plt.cm.viridis(i)) for i in np.linspace(0, 1, 8)],
    "地球科学配色": [to_hex(plt.cm.terrain(i)) for i in np.linspace(0, 1, 8)],
    "随机生成": None,
    "全部Python色彩": list(CSS4_COLORS.keys())
}

def load_custom_palettes():
    if os.path.exists(CUSTOM_PALETTE_FILE):
        with open(CUSTOM_PALETTE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_custom_palettes(custom_palettes):
    with open(CUSTOM_PALETTE_FILE, "w") as f:
        json.dump(custom_palettes, f)

class ColorApp:
    def __init__(self, master):
        self.master = master
        master.title("色彩搭配助手")

        self.custom_palettes = load_custom_palettes()
        self.update_palette_options()

        self.style_var = tk.StringVar(value="高对比度")
        self.colors = self.get_palette(self.style_var.get())
        self.color_buttons = []

        ttk.Label(master, text="配色风格:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.style_menu = ttk.Combobox(master, textvariable=self.style_var, values=self.palette_keys, state="readonly")
        self.style_menu.grid(row=0, column=1, padx=5, pady=5)
        self.style_menu.bind("<<ComboboxSelected>>", self.update_palette)

        self.canvas = tk.Canvas(master, width=400, height=50)
        self.canvas.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        ttk.Button(master, text="复制代码", command=self.copy_code).grid(row=2, column=0, pady=10)
        ttk.Button(master, text="保存色板", command=self.save_palette).grid(row=2, column=1, pady=10)
        ttk.Button(master, text="添加自定义", command=self.add_custom_palette).grid(row=2, column=2, pady=10)
        ttk.Button(master, text="删除自定义", command=self.delete_custom_palette).grid(row=2, column=3, pady=10)

        self.draw_palette()

    def update_palette_options(self):
        self.palette_keys = list(PALETTES.keys()) + list(self.custom_palettes.keys())

    def get_palette(self, name):
        if name == "随机生成":
            return ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(8)]
        elif name in self.custom_palettes:
            return self.custom_palettes[name]
        colors = PALETTES.get(name, [])
        if isinstance(colors, list) and isinstance(colors[0], tuple):
            return [to_hex(c) for c in colors]
        return colors

    def update_palette(self, event=None):
        self.colors = self.get_palette(self.style_var.get())
        self.draw_palette()

    def draw_palette(self):
        for btn in getattr(self, "color_buttons", []):
            btn.destroy()
        self.color_buttons.clear()
        self.canvas.delete("all")

        if self.style_var.get() == "全部Python色彩":
            self.draw_all_colors()
        else:
            self.canvas.config(width=400, height=50)
            self.draw_color_bar()

    def draw_color_bar(self):
        w = 400 // len(self.colors)
        for i, color in enumerate(self.colors):
            self.canvas.create_rectangle(i * w, 0, (i + 1) * w, 50, fill=color, outline='')

    def draw_all_colors(self):
        color_list = PALETTES["全部Python色彩"]
        cols = 10
        w, h = 80, 40
        font_size = 8

        rows = (len(color_list) + cols - 1) // cols
        canvas_height = rows * h
        canvas_width = cols * w
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas.delete("all")

        for i, name in enumerate(color_list):
            try:
                color_hex = to_hex(to_rgb(name))
            except ValueError:
                continue

            row = i // cols
            col = i % cols
            x1, y1 = col * w, row * h
            x2, y2 = x1 + w, y1 + h

            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color_hex, outline='black')

            # 自动判断文字颜色（浅色背景用黑字，深色背景用白字）
            r, g, b = to_rgb(color_hex)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            text_color = "#000000" if brightness > 0.5 else "#FFFFFF"

            # 居中显示颜色代码
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=color_hex, font=("Arial", font_size),
                                    fill=text_color)

            self.canvas.tag_bind(rect, "<Button-1>", lambda e, c=color_hex: self.copy_color_code(c))

    def copy_color_code(self, code):
        self.master.clipboard_clear()
        self.master.clipboard_append(code)
        messagebox.showinfo("复制成功", f"{code} 已复制到剪贴板！")

    def copy_code(self):
        code = f"colors = {self.colors}"
        self.master.clipboard_clear()
        self.master.clipboard_append(code)
        messagebox.showinfo("复制成功", "色板代码已复制到剪贴板！")

    def save_palette(self):
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON文件", "*.json")])
        if file:
            with open(file, "w") as f:
                json.dump(self.colors, f)
            messagebox.showinfo("保存成功", f"已保存至 {file}")

    def add_custom_palette(self):
        name = simpledialog.askstring("自定义配色", "请输入配色名称：")
        if not name:
            return
        colors = simpledialog.askstring("输入颜色", "请输入颜色代码（用英文逗号分隔，如 #FF0000,#00FF00,#0000FF）：")
        if not colors:
            return
        try:
            color_list = [c.strip() for c in colors.split(",")]
            _ = [to_hex(to_rgb(c)) for c in color_list]  # 验证颜色合法性
        except Exception as e:
            messagebox.showerror("错误", f"颜色格式有误：{e}")
            return

        self.custom_palettes[name] = color_list
        save_custom_palettes(self.custom_palettes)
        self.update_palette_options()
        self.style_menu.config(values=self.palette_keys)
        messagebox.showinfo("添加成功", f"自定义配色“{name}”已保存")
        self.style_var.set(name)
        self.update_palette()

    def delete_custom_palette(self):
        name = self.style_var.get()
        if name in self.custom_palettes:
            if messagebox.askyesno("删除确认", f"是否删除自定义配色“{name}”？"):
                del self.custom_palettes[name]
                save_custom_palettes(self.custom_palettes)
                self.update_palette_options()
                self.style_menu.config(values=self.palette_keys)
                self.style_var.set("高对比度")
                self.update_palette()
        else:
            messagebox.showinfo("提示", "当前选择不是自定义配色，无法删除。")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorApp(root)
    root.resizable(False, False)
    root.mainloop()
