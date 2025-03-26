import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import easyocr
import os
import threading


class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR文字识别工具")
        self.root.geometry("600x400")

        # 初始化OCR阅读器（先设为None）
        self.reader = None

        # 创建界面组件
        self.create_widgets()

        # 在后台初始化OCR模型
        self.initialize_ocr()

    def create_widgets(self):
        # 图片选择区域
        ttk.Label(self.root, text="图片路径：").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.img_entry = ttk.Entry(self.root, width=50)
        self.img_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="选择图片", command=self.select_image).grid(row=0, column=2, padx=5, pady=5)

        # 保存路径区域
        ttk.Label(self.root, text="保存路径：").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.save_entry = ttk.Entry(self.root, width=50)
        self.save_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="选择路径", command=self.select_save_path).grid(row=1, column=2, padx=5, pady=5)

        # 状态显示
        self.status_label = ttk.Label(self.root, text="准备就绪", foreground="gray")
        self.status_label.grid(row=2, column=0, columnspan=3, pady=10)

        # 执行按钮
        self.run_btn = ttk.Button(self.root, text="开始识别", command=self.run_ocr, state=tk.DISABLED)
        self.run_btn.grid(row=3, column=1, pady=20)

    def initialize_ocr(self):
        """后台初始化OCR模型"""
        self.status_label.config(text="正在初始化OCR引擎...", foreground="blue")
        threading.Thread(target=self.load_ocr_model, daemon=True).start()

    def load_ocr_model(self):
        try:
            self.reader = easyocr.Reader(['ch_sim', 'en'])
            self.root.after(0, lambda: [
                self.run_btn.config(state=tk.NORMAL),
                self.status_label.config(text="准备就绪", foreground="green")
            ])
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"模型加载失败: {str(e)}"))

    def select_image(self):
        filetypes = (
            ('图片文件', '*.png *.jpg *.jpeg *.bmp'),
            ('所有文件', '*.*')
        )
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.img_entry.delete(0, tk.END)
            self.img_entry.insert(0, path)

    def select_save_path(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=(("文本文件", "*.txt"), ("所有文件", "*.*"))
        )
        if path:
            self.save_entry.delete(0, tk.END)
            self.save_entry.insert(0, path)

    def run_ocr(self):
        """启动OCR识别线程"""
        img_path = self.img_entry.get()
        save_path = self.save_entry.get()

        # 输入验证
        if not os.path.isfile(img_path):
            self.show_error("请选择有效的图片文件")
            return
        if not save_path:
            self.show_error("请指定保存路径")
            return

        # 禁用按钮并更新状态
        self.run_btn.config(state=tk.DISABLED)
        self.status_label.config(text="正在识别...", foreground="blue")

        # 在后台线程执行OCR
        threading.Thread(target=self.process_ocr, args=(img_path, save_path), daemon=True).start()

    def process_ocr(self, img_path, save_path):
        try:
            # 执行OCR识别
            results = self.reader.readtext(img_path)
            texts = [result[1] for result in results]

            # 创建输出目录
            output_dir = os.path.dirname(save_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 保存结果
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(texts))

            self.root.after(0, lambda: [
                self.status_label.config(text="识别完成！", foreground="green"),
                self.run_btn.config(state=tk.NORMAL),
                messagebox.showinfo("完成", f"结果已保存至：\n{save_path}")
            ])
        except Exception as e:
            self.root.after(0, lambda: [
                self.show_error(f"识别失败: {str(e)}"),
                self.run_btn.config(state=tk.NORMAL)
            ])

    def show_error(self, message):
        self.status_label.config(text=message, foreground="red")
        messagebox.showerror("错误", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
