import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import random
import os

# ===================== 数据存储 =====================
DATA_FILE = "word_data.json"
STUDENT_FILE = "student_data.json"

def load_words():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_words(words):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

def load_students():
    if os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_students(lst):
    with open(STUDENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)

# ===================== 主程序 =====================
class WordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("英语课堂抽词工具")
        self.root.geometry("900x650")

        self.words = load_words()
        self.students = load_students()
        self.remaining = list(self.words.keys())

        # 标签栏
        self.tab_control = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text="随机抽词")
        self.tab_control.add(self.tab2, text="随机点名")
        self.tab_control.add(self.tab3, text="单词管理")
        self.tab_control.pack(expand=1, fill="both")

        self.init_tab1()
        self.init_tab2()
        self.init_tab3()

    # ===================== 抽词页面 =====================
    def init_tab1(self):
        frame = ttk.Frame(self.tab1)
        frame.pack(pady=15, fill='x', padx=20)

        ttk.Label(frame, text="每组数量：").grid(row=0, column=0, padx=5)
        self.per_num = ttk.Combobox(frame, values=[1,2,3,4,5], width=5)
        self.per_num.current(2)
        self.per_num.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="显示模式：").grid(row=0, column=2, padx=5)
        self.mode = ttk.Combobox(frame, values=["仅英文","仅中文","英汉对照"], width=12)
        self.mode.current(2)
        self.mode.grid(row=0, column=3, padx=5)

        ttk.Button(frame, text="重置顺序", command=self.reset_queue).grid(row=0, column=4, padx=5)

        # 展示区
        self.show_frame = ttk.Frame(self.tab1)
        self.show_frame.pack(pady=20, fill='both', expand=True, padx=30)
        self.word_labels = []

        # 下一组按钮
        ttk.Button(self.tab1, text="下一组单词", command=self.next_word, width=20).pack(pady=10)

    def reset_queue(self):
        self.remaining = list(self.words.keys())
        for w in self.word_labels:
            w.destroy()
        self.word_labels = []
        ttk.Label(self.show_frame, text="抽取顺序已重置").pack()

    def next_word(self):
        for w in self.word_labels:
            w.destroy()
        self.word_labels = []

        if not self.words:
            ttk.Label(self.show_frame, text="请先导入单词").pack()
            return

        if not self.remaining:
            ttk.Label(self.show_frame, text="✅ 所有单词已抽取完成", font=("",20,"bold"), foreground="green").pack()
            return

        n = int(self.per_num.get())
        count = min(n, len(self.remaining))
        selected = []
        for _ in range(count):
            idx = random.randint(0, len(self.remaining)-1)
            selected.append(self.remaining.pop(idx))

        mode = self.mode.get()
        for en in selected:
            cn = self.words[en]
            if mode == "仅英文":
                txt = en
            elif mode == "仅中文":
                txt = cn
            else:
                txt = f"{en} — {cn}"
            lb = ttk.Label(self.show_frame, text=txt, font=("",24,"bold"))
            lb.pack(pady=8)
            self.word_labels.append(lb)

    # ===================== 点名页面 =====================
    def init_tab2(self):
        frame = ttk.Frame(self.tab2)
        frame.pack(pady=15, fill='x', padx=20)

        ttk.Label(frame, text="班级名单（逗号/空格分隔）：").pack(anchor='w')
        self.stu_entry = scrolledtext.ScrolledText(frame, height=4)
        self.stu_entry.pack(fill='x', pady=5)
        self.stu_entry.insert("end", ",".join(self.students))

        ttk.Button(frame, text="保存名单", command=self.save_stu).pack()

        self.stu_show = ttk.Label(self.tab2, text="", font=("",26,"bold"), foreground="orange")
        self.stu_show.pack(pady=40)

        ttk.Button(self.tab2, text="随机抽取学生", command=self.rand_stu).pack()

    def save_stu(self):
        txt = self.stu_entry.get("1.0", "end").strip()
        import re
        lst = re.split(r'[，,\s]+', txt)
        lst = [x.strip() for x in lst if x.strip()]
        self.students = lst
        save_students(lst)
        messagebox.showinfo("完成", "已保存名单")

    def rand_stu(self):
        if not self.students:
            self.stu_show.config(text="请先保存名单")
            return
        name = random.choice(self.students)
        self.stu_show.config(text=f"请 {name} 同学回答")

    # ===================== 单词管理 =====================
    def init_tab3(self):
        # 文件导入
        ttk.Button(self.tab3, text="导入单词文件(.txt)", command=self.import_txt).pack(pady=5)
        ttk.Button(self.tab3, text="导出单词备份", command=self.export_txt).pack(pady=5)
        ttk.Button(self.tab3, text="查看单词库", command=self.show_lib).pack(pady=5)
        ttk.Button(self.tab3, text="清空单词库", command=self.clear_all).pack(pady=5)

    def import_txt(self):
        path = filedialog.askopenfilename(filetypes=[("文本文档", "*.txt")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            with open(path, 'r', encoding='gbk') as f:
                lines = f.readlines()

        cnt = 0
        for line in lines:
            line = line.strip()
            if not line: continue
            parts = line.split()
            if len(parts) < 2: continue
            en = parts[0].lower()
            cn = " ".join(parts[1:])
            self.words[en] = cn
            cnt += 1
        save_words(self.words)
        self.reset_queue()
        messagebox.showinfo("导入成功", f"共导入 {cnt} 个单词")

    def export_txt(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文档", "*.txt")])
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            for en, cn in sorted(self.words.items()):
                f.write(f"{en} {cn}\n")
        messagebox.showinfo("完成", "单词已导出")

    def clear_all(self):
        if not messagebox.askyesno("确认", "确定清空所有单词？"):
            return
        self.words = {}
        save_words(self.words)
        self.remaining = []
        messagebox.showinfo("完成", "已清空")

    def show_lib(self):
        win = tk.Toplevel(self.root)
        win.title("单词库")
        win.geometry("700x500")

        ttk.Label(win, text="搜索：").pack()
        search_var = tk.StringVar()
        entry = ttk.Entry(win, textvariable=search_var)
        entry.pack(fill='x', padx=20)

        frame = ttk.Frame(win)
        frame.pack(fill='both', expand=True, pady=10)

        scroll = ttk.Scrollbar(frame)
        scroll.pack(side='right', fill='y')
        listbox = tk.Listbox(frame, font=("",14), yscrollcommand=scroll.set)
        listbox.pack(fill='both', expand=True)
        scroll.config(command=listbox.yview)

        def show_list(key=""):
            listbox.delete(0, tk.END)
            words = sorted(self.words.items())
            for en, cn in words:
                if key and key not in en:
                    continue
                listbox.insert(tk.END, f"{en:<18} {cn}")

        show_list()
        search_var.trace("w", lambda *args: show_list(search_var.get().strip()))

if __name__ == "__main__":
    root = tk.Tk()
    app = WordApp(root)
    root.mainloop()