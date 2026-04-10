import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import random
import os

# ===================== 数据存储 =====================
DATA_FILE = "word_library.json"
STUDENT_FILE = "student_data.json"

def load_all_library():
    """加载所有词表"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"默认词表": {}}

def save_all_library(data):
    """保存所有词表"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
        self.root.title("英语课堂抽词工具【多词表版】")
        self.root.geometry("950x700")

        # 核心数据：所有词表
        self.library = load_all_library()
        # 当前选中的词表名
        self.current_lib = list(self.library.keys())[0] if self.library else ""
        # 当前词表的剩余单词
        self.remaining = list(self.library[self.current_lib].keys()) if self.current_lib else []
        # 学生名单
        self.students = load_students()

        # 标签栏
        self.tab_control = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab3 = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text="随机抽词")
        self.tab_control.add(self.tab2, text="随机点名")
        self.tab_control.add(self.tab3, text="词表管理")
        self.tab_control.pack(expand=1, fill="both", padx=5, pady=5)

        self.init_tab1()
        self.init_tab2()
        self.init_tab3()
        self.refresh_lib_combobox()

    # ===================== 抽词页面 =====================
    def init_tab1(self):
        # 顶部控制栏
        control_frame = ttk.Frame(self.tab1)
        control_frame.pack(pady=10, fill='x', padx=20)

        # 词表选择
        ttk.Label(control_frame, text="当前词表：").grid(row=0, column=0, padx=5)
        self.lib_cb = ttk.Combobox(control_frame, state="readonly", width=18)
        self.lib_cb.grid(row=0, column=1, padx=5)
        self.lib_cb.bind("<<ComboboxSelected>>", self.switch_library)

        # 每组数量
        ttk.Label(control_frame, text="每组数量：").grid(row=0, column=2, padx=5)
        self.per_num = ttk.Combobox(control_frame, values=[1,2,3,4,5], width=5)
        self.per_num.current(2)
        self.per_num.grid(row=0, column=3, padx=5)

        # 显示模式
        ttk.Label(control_frame, text="显示模式：").grid(row=0, column=4, padx=5)
        self.mode = ttk.Combobox(control_frame, values=["仅英文","仅中文","英汉对照"], width=12)
        self.mode.current(2)
        self.mode.grid(row=0, column=5, padx=5)

        # 功能按钮
        ttk.Button(control_frame, text="重置抽取", command=self.reset_queue).grid(row=0, column=6, padx=5)

        # 单词展示区
        self.show_frame = ttk.Frame(self.tab1)
        self.show_frame.pack(pady=20, fill='both', expand=True, padx=30)
        self.word_labels = []

        # 抽取按钮
        ttk.Button(self.tab1, text="下一组单词", command=self.next_word, width=22).pack(pady=10)

    def refresh_lib_combobox(self):
        """刷新词表下拉框"""
        lib_names = list(self.library.keys())
        self.lib_cb.config(values=lib_names)
        if lib_names:
            self.lib_cb.current(lib_names.index(self.current_lib))

    def switch_library(self, event=None):
        """切换词表"""
        self.current_lib = self.lib_cb.get()
        self.reset_queue()
        messagebox.showinfo("切换成功", f"已切换至词表：{self.current_lib}")

    def reset_queue(self):
        """重置当前词表抽取顺序"""
        if not self.current_lib:
            return
        self.remaining = list(self.library[self.current_lib].keys())
        for w in self.word_labels:
            w.destroy()
        self.word_labels = []
        tip = ttk.Label(self.show_frame, text=f"【{self.current_lib}】抽取顺序已重置")
        tip.pack()
        self.word_labels.append(tip)

    def next_word(self):
        """抽取下一组单词"""
        # 清空原有显示
        for w in self.word_labels:
            w.destroy()
        self.word_labels = []

        # 无词表判断
        if not self.current_lib:
            ttk.Label(self.show_frame, text="请先创建并选择词表", font=("",18)).pack()
            return

        current_words = self.library[self.current_lib]
        # 无单词判断
        if not current_words:
            ttk.Label(self.show_frame, text="当前词表暂无单词，请先导入", font=("",18)).pack()
            return

        # 全部抽完判断
        if not self.remaining:
            finish_label = ttk.Label(
                self.show_frame, 
                text="✅ 当前词表所有单词已抽取完成", 
                font=("",22,"bold"), 
                foreground="green"
            )
            finish_label.pack(pady=10)
            self.word_labels.append(finish_label)
            return

        # 抽取单词
        n = int(self.per_num.get())
        count = min(n, len(self.remaining))
        selected = []
        for _ in range(count):
            idx = random.randint(0, len(self.remaining)-1)
            selected.append(self.remaining.pop(idx))

        # 显示单词
        mode = self.mode.get()
        for en in selected:
            cn = current_words[en]
            if mode == "仅英文":
                txt = en
            elif mode == "仅中文":
                txt = cn
            else:
                txt = f"{en} — {cn}"
            lb = ttk.Label(self.show_frame, text=txt, font=("",26,"bold"))
            lb.pack(pady=10)
            self.word_labels.append(lb)

    # ===================== 点名页面 =====================
    def init_tab2(self):
        frame = ttk.Frame(self.tab2)
        frame.pack(pady=15, fill='x', padx=20)

        ttk.Label(frame, text="班级名单（逗号/空格/换行分隔）：").pack(anchor='w')
        self.stu_entry = scrolledtext.ScrolledText(frame, height=5)
        self.stu_entry.pack(fill='x', pady=8)
        self.stu_entry.insert("end", "\n".join(self.students))

        ttk.Button(frame, text="保存学生名单", command=self.save_stu).pack(pady=5)

        self.stu_show = ttk.Label(self.tab2, text="", font=("",30,"bold"), foreground="#ff6600")
        self.stu_show.pack(pady=50)

        ttk.Button(self.tab2, text="随机抽取学生", command=self.rand_stu, width=20).pack()

    def save_stu(self):
        txt = self.stu_entry.get("1.0", "end").strip()
        import re
        lst = re.split(r'[，,\s\n]+', txt)
        lst = [x.strip() for x in lst if x.strip()]
        self.students = lst
        save_students(lst)
        messagebox.showinfo("保存成功", "学生名单已永久保存")

    def rand_stu(self):
        if not self.students:
            self.stu_show.config(text="请先保存学生名单")
            return
        name = random.choice(self.students)
        self.stu_show.config(text=f"请 👉 {name} 👈 同学回答")

    # ===================== 词表管理页面 =====================
    def init_tab3(self):
        # 词表操作栏
        lib_opt_frame = ttk.Frame(self.tab3)
        lib_opt_frame.pack(pady=10, fill='x', padx=20)

        ttk.Button(lib_opt_frame, text="新建词表", command=self.create_library).grid(row=0, column=0, padx=8)
        ttk.Button(lib_opt_frame, text="删除当前词表", command=self.delete_library).grid(row=0, column=1, padx=8)
        
        # 当前词表操作
        ttk.Label(self.tab3, text="当前词表操作", font=("",14,"bold")).pack(pady=8)
        btn_frame = ttk.Frame(self.tab3)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="导入TXT单词", command=self.import_txt, width=18).grid(row=0, column=0, padx=10, pady=8)
        ttk.Button(btn_frame, text="导出当前词表", command=self.export_txt, width=18).grid(row=0, column=1, padx=10, pady=8)
        ttk.Button(btn_frame, text="查看单词库", command=self.show_lib, width=18).grid(row=1, column=0, padx=10, pady=8)
        ttk.Button(btn_frame, text="清空当前词表", command=self.clear_current_lib, width=18).grid(row=1, column=1, padx=10, pady=8)

        # 说明
        ttk.Label(
            self.tab3, 
            text="TXT格式：每行一个单词  英文 中文（空格分隔）\n示例：apple 苹果 | do done 做（完成式）",
            font=("",12)
        ).pack(pady=20)

    def create_library(self):
        """新建词表"""
        name = tk.simpledialog.askstring("新建词表", "请输入词表名称：")
        if not name:
            return
        if name in self.library:
            messagebox.showerror("错误", "该词表名称已存在")
            return
        self.library[name] = {}
        save_all_library(self.library)
        self.current_lib = name
        self.refresh_lib_combobox()
        self.reset_queue()
        messagebox.showinfo("成功", f"词表【{name}】创建完成")

    def delete_library(self):
        """删除当前词表"""
        if not self.current_lib:
            return
        if len(self.library) <= 1:
            messagebox.showerror("错误", "至少保留一个词表")
            return
        if not messagebox.askyesno("确认", f"确定删除词表【{self.current_lib}】？\n删除后数据无法恢复！"):
            return
        del self.library[self.current_lib]
        save_all_library(self.library)
        self.current_lib = list(self.library.keys())[0]
        self.refresh_lib_combobox()
        self.reset_queue()
        messagebox.showinfo("成功", "词表已删除")

    def import_txt(self):
        """导入单词到当前词表"""
        if not self.current_lib:
            messagebox.showwarning("提示", "请先选择词表")
            return
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
        current_words = self.library[self.current_lib]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            en = parts[0].lower()
            cn = " ".join(parts[1:])
            current_words[en] = cn
            cnt += 1
        save_all_library(self.library)
        self.reset_queue()
        messagebox.showinfo("导入成功", f"已向【{self.current_lib}】导入 {cnt} 个单词")

    def export_txt(self):
        """导出当前词表"""
        if not self.current_lib or not self.library[self.current_lib]:
            messagebox.showwarning("提示", "当前词表无单词可导出")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            filetypes=[("文本文档", "*.txt")],
            initialfile=f"{self.current_lib}.txt"
        )
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            for en, cn in sorted(self.library[self.current_lib].items()):
                f.write(f"{en} {cn}\n")
        messagebox.showinfo("导出成功", f"【{self.current_lib}】已导出")

    def clear_current_lib(self):
        """清空当前词表"""
        if not self.current_lib:
            return
        if not messagebox.askyesno("确认", f"确定清空【{self.current_lib}】所有单词？"):
            return
        self.library[self.current_lib] = {}
        save_all_library(self.library)
        self.reset_queue()
        messagebox.showinfo("成功", "当前词表已清空")

    def show_lib(self):
        """查看当前词表单词（字典序+搜索）"""
        if not self.current_lib:
            messagebox.showwarning("提示", "请先选择词表")
            return
        current_words = self.library[self.current_lib]
        win = tk.Toplevel(self.root)
        win.title(f"单词库 - {self.current_lib}")
        win.geometry("750x550")

        # 搜索框
        ttk.Label(win, text="搜索单词：").pack(pady=5)
        search_var = tk.StringVar()
        entry = ttk.Entry(win, textvariable=search_var, font=("",12))
        entry.pack(fill='x', padx=25)

        # 列表展示
        frame = ttk.Frame(win)
        frame.pack(fill='both', expand=True, pady=10, padx=25)

        scroll = ttk.Scrollbar(frame)
        scroll.pack(side='right', fill='y')
        listbox = tk.Listbox(frame, font=("",14), yscrollcommand=scroll.set)
        listbox.pack(fill='both', expand=True)
        scroll.config(command=listbox.yview)

        def show_list(key=""):
            listbox.delete(0, tk.END)
            words = sorted(current_words.items())
            for en, cn in words:
                if key and key not in en:
                    continue
                listbox.insert(tk.END, f"{en:<20} {cn}")
            if not listbox.size():
                listbox.insert(tk.END, "暂无匹配单词")

        show_list()
        search_var.trace("w", lambda *args: show_list(search_var.get().strip()))

# ===================== 简化弹窗依赖 =====================
try:
    import tkinter.simpledialog as simpledialog
except:
    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = WordApp(root)
    root.mainloop()