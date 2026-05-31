"""
暖心便签爱心 — 模仿"温馨提示弹窗30次"风格
每张便签 = 正常 Toplevel 窗口（有标题栏），从屏幕四周飞入汇聚成爱心
"""
import tkinter as tk
import math
import random

# ========== 配置（匹配温馨提示弹窗源代码） ==========
HEART_SCALE = 20           # 爱心大小（匹配源代码 scale=20）
POPUP_COUNT = 30           # 弹窗数量
ANIMATION_TICK = 50        # 帧间隔 ms（~20fps，减少刷新负担）
FLY_IN_BASE_SPEED = 0.035  # 飞行速度（提速，减少总帧数）
FONT_FAMILY = "楷体"
FONT_SIZE = 18
WIN_W = 220
WIN_H = 50

# 单行消息（匹配源代码风格）
MESSAGES = [
    "多喝水哦~", "保持微笑呀", "好好爱自己", "保持好心情", "愿你平安喜乐",
    "一切都会好起来的", "勇敢一点", "你很棒", "记得吃水果", "金榜题名",
    "你是独一无二的光", "早点休息", "所有烦恼都消失", "梦想成真", "少熬夜",
    "天冷了多穿衣服", "今天过得开心嘛", "万事如意", "加油你可以的", "你好棒为你骄傲",
    "开心每一天幸福永远", "幸运之星照耀着你", "美好时光值得珍惜", "温暖如春心中有爱",
    "阳光灿烂心情明朗", "甜蜜生活快乐相随", "幸福满满无忧无虑", "快乐相伴永不孤单",
    "微笑面对一切会好", "梦想启航扬帆远行",
]

# 命名颜色（匹配源代码风格）
COLORS = [
    "pink", "lightblue", "lightgreen", "yellow", "lightcoral", "lightgray",
    "lavender", "coral", "bisque", "aquamarine", "plum", "honeydew", "mistyrose",
    "oldlace", "skyblue", "lightpink", "lightyellow", "peachpuff", "thistle",
    "wheat", "palegreen", "powderblue", "rosybrown", "tan", "khaki",
    "lightcyan", "lightsteelblue", "paleturquoise", "seashell", "azure",
]


# ========== 爱心点生成（完全匹配源代码算法） ==========
def generate_heart_points(num_points, scale=HEART_SCALE):
    """生成爱心轮廓坐标点 —— 与温馨提示弹窗源代码完全一致"""
    points = []
    for i in range(num_points):
        t = 2 * math.pi * i / num_points
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        points.append((x * scale, -y * scale))
    return points


# ========== 便签窗口 ==========
class NoteWindow:
    """独立的 Toplevel 便签窗口（匹配温馨提示弹窗风格）"""

    def __init__(self, root, msg, color, start_x, start_y,
                 target_x, target_y, win_w, win_h, on_click=None):
        self.root = root
        self.target_x = target_x
        self.target_y = target_y
        self.start_x = start_x
        self.start_y = start_y
        self.progress = 0.0
        self.speed = FLY_IN_BASE_SPEED * random.uniform(0.5, 1.5)
        self.arrived = False

        # 正常窗口（有标题栏），匹配源代码风格
        self.win = tk.Toplevel(root)
        self.win.title('温馨提示')
        self.win.attributes("-topmost", True)
        self.win.geometry(f"{win_w}x{win_h}+{start_x}+{start_y}")

        # Label 使用 width/height 参数，匹配源代码写法
        label = tk.Label(
            self.win,
            text=msg,
            bg=color,
            font=(FONT_FAMILY, FONT_SIZE, "normal"),
            width=25, height=4,
        )
        label.pack()

        # 点击便签任意位置退出
        if on_click:
            label.bind("<Button-1>", lambda e: on_click())
            self.win.bind("<Button-1>", lambda e: on_click())

        # 点击关闭按钮(X)也要彻底退出，防止后台残留进程
        self.win.protocol("WM_DELETE_WINDOW", on_click if on_click else self.destroy)

    def current_pos(self):
        if self.arrived:
            return self.target_x, self.target_y
        t = self.progress
        eased = 1 - (1 - t) ** 3  # ease-out³：开始快，末尾吸附
        cx = int(self.start_x + (self.target_x - self.start_x) * eased)
        cy = int(self.start_y + (self.target_y - self.start_y) * eased)
        return cx, cy

    def update_position(self):
        if self.arrived:
            return
        cx, cy = self.current_pos()
        self.win.geometry(f"+{cx}+{cy}")

    def destroy(self):
        try:
            self.win.destroy()
        except Exception:
            pass


# ========== 主应用 ==========
class HeartApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        self.cx = self.sw // 2
        self.cy = self.sh // 2

        self.win_w, self.win_h = WIN_W, WIN_H
        self.note_wins = []
        self.notes = []
        self.completed = False

        # 退出方式（Escape 始终可用）
        self.root.bind_all("<Escape>", lambda e: self.safe_exit())

        # 先显示前置弹窗
        self.create_main_popup()
        self.root.mainloop()

    # 劝说文案（每次点击不要 → 换一句 + 按钮跑位）
    PERSUADE_TEXTS = [
        "别这样嘛~ (｡•́︿•̀｡)",
        "再想想？(◍•ᴗ•◍)",
        "选好的吧！(๑•̀ㅂ•́)و✧",
        "不要拒绝啦~ (´;ω;`)",
        "你忍心嘛 (╥﹏╥)",
        "点一下好的嘛 (๑´ㅂ`๑)",
        "真的很暖的！(≧∇≦)ﾉ",
        "试一下又不会~ (◕ᴗ◕✿)",
        "你会喜欢的 (｡･ω･｡)ﾉ♡",
        "就点一下好的 ( •̀ ω •́ )✧",
        "不点好的会后悔 (ᗒᗣᗕ)՞",
        "乖，选好的 (´▽`ʃ♡ƪ)",
        "看看爱心嘛 (◠‿◠✿)",
        "免费的哦~ (＾▽＾)",
        "只耽误几秒 (•́‿•̀)",
        "包你满意！ヽ(✿ﾟ▽ﾟ)ノ",
    ]

    def create_main_popup(self):
        """前置窗口：每天都要开心点"""
        self.main_win = tk.Toplevel(self.root)
        self.main_win.title('温馨提醒')
        self.main_win.attributes("-topmost", True)
        self.main_win.configure(bg="lightblue")

        self.main_msg = tk.Label(
            self.main_win, text="每天都要开心点！",
            bg="lightblue", font=('楷体', 18), fg="#333",
        )
        self.main_msg.pack(pady=(30, 15))

        # "好的" 按钮固定
        self.agree_btn = tk.Button(
            self.main_win, text="好的", bg="lightgreen",
            font=('宋体', 13), width=10,
            command=self.on_agree,
        )

        # "不要" 按钮用 place 定位（方便随机移动）
        self.reject_btn = tk.Button(
            self.main_win, text="不要", bg="lightcoral",
            font=('宋体', 13), width=10,
            command=self.on_reject,
        )
        self.persuade_idx = 0

        self._resize_main_win("每天都要开心点！")

        self.main_win.protocol("WM_DELETE_WINDOW", self.safe_exit)

    def _resize_main_win(self, text):
        """根据文字长度调整窗口大小，按钮左右对称"""
        text_w = len(text) * 18 + 80
        w = max(360, text_w)
        h = 160
        x = (self.sw - w) // 2
        y = (self.sh - h) // 2
        self.main_win.geometry(f"{w}x{h}+{x}+{y}")
        # 按钮左右对称，间距 120px（不挨着）
        btn_y = 85
        gap = 60  # 距离中心各 60px
        self.agree_btn.place(x=w//2 + gap, y=btn_y, anchor="center")
        self.reject_btn.place(x=w//2 - gap, y=btn_y, anchor="center")

    def on_agree(self):
        """点击好的 → 关闭前置窗口，启动爱心动画"""
        self.main_win.destroy()
        self.init_heart()
        self.root.after(300, self.animate)

    def on_reject(self):
        """点击不要 → 文字变劝说 + 按钮随机跑位"""
        # 换劝说文字
        text = self.PERSUADE_TEXTS[self.persuade_idx % len(self.PERSUADE_TEXTS)]
        self.persuade_idx += 1
        self.main_msg.config(text=text)
        self._resize_main_win(text)

        # 按钮在窗口内随机移动
        w = self.main_win.winfo_width()
        h = self.main_win.winfo_height()
        rx = random.randint(20, w - 100)
        ry = random.randint(60, h - 50)
        self.reject_btn.place(x=rx, y=ry, anchor="center")

    def init_heart(self):
        """初始化爱心数据"""
        heart_points = generate_heart_points(POPUP_COUNT, HEART_SCALE)
        heart_points.sort(key=lambda p: p[0]**2 + p[1]**2)
        print(f"爱心轮廓点: {len(heart_points)} 个, scale={HEART_SCALE}")

        self.notes = []
        for i, (hx, hy) in enumerate(heart_points):
            msg = MESSAGES[i % len(MESSAGES)]
            color = COLORS[i % len(COLORS)]
            sx = self.cx - self.win_w // 2 + random.randint(-15, 15)
            sy = self.cy - self.win_h // 2 + random.randint(-10, 10)
            self.notes.append({
                "msg": msg, "color": color,
                "start_x": sx, "start_y": sy,
                "target_x": self.cx + int(hx) - self.win_w // 2,
                "target_y": self.cy + int(hy) - self.win_h // 2,
            })

        self.total = len(self.notes)
        self.next_idx = 0
        self.spawn_timer = 0
        print(f"共 {self.total} 张便签（从中心绽放）")

    def safe_exit(self):
        """关闭爱心，先弹寄语再退出（幂等，防止重复触发）"""
        if getattr(self, '_exiting', False):
            return
        self._exiting = True
        # 销毁所有便签窗口
        for nw in self.note_wins:
            nw.destroy()
        self.note_wins.clear()
        # 弹出寄语
        self.show_final_message()

    def _do_exit(self):
        """最终退出（幂等）"""
        if getattr(self, '_exited', False):
            return
        self._exited = True
        try:
            self.root.destroy()
        except Exception:
            pass

    def spawn_note(self):
        if self.next_idx >= self.total:
            return
        nd = self.notes[self.next_idx]
        self.next_idx += 1
        nw = NoteWindow(self.root, nd["msg"], nd["color"],
                        nd["start_x"], nd["start_y"],
                        nd["target_x"], nd["target_y"],
                        self.win_w, self.win_h,
                        on_click=self.safe_exit)
        self.note_wins.append(nw)

    def animate(self):
        # 从中心逐个发射（每 3 帧一个，约 150ms 间隔，减少同时动画数量）
        if self.next_idx < self.total:
            self.spawn_timer += 1
            if self.spawn_timer >= 3:
                self.spawn_timer = 0
                self.spawn_note()

        # 更新飞行中便签的位置
        still_flying = 0
        for nw in self.note_wins:
            if not nw.arrived:
                nw.progress += nw.speed
                if nw.progress >= 1.0:
                    nw.progress = 1.0
                    nw.arrived = True
                nw.update_position()
            if not nw.arrived:
                still_flying += 1

        # 全部到达，静置展示
        if self.next_idx >= self.total and still_flying == 0 and not self.completed:
            self.completed = True
            return

        self.root.after(ANIMATION_TICK, self.animate)

    def show_final_message(self):
        """关闭爱心后弹出随机关心文字，点击退出"""
        texts = [
            "不管今天过得怎样，明天都是崭新的开始，好好爱自己。",
            "你值得这世间所有的美好，别忘了每天都给自己一个微笑。",
            "累了就停下歇歇，你不是一个人在扛，总有人在牵挂着你。",
            "生活也许不完美，但总有小确幸藏在角落里等你发现。",
            "今天的你也辛苦啦，泡杯热茶，听首喜欢的歌，放松一下吧。",
            "记得按时吃饭、早点睡觉，你的健康是很多人最大的心愿。",
            "不必事事完美，你已经做得很好了，对自己温柔一点。",
            "愿你三冬暖，愿你春不寒，愿你天黑有灯，下雨有伞。",
            "无论走到哪里，都别忘了带上你的笑容和好心情。",
            "世界很大，你很珍贵，每一天都要为自己开开心心地过。",
        ]
        msg = random.choice(texts)

        w = tk.Toplevel(self.root)
        w.title('❤ 暖心寄语')
        w.attributes("-topmost", True)
        w.configure(bg="#FFF5F5")

        win_w, win_h = 420, 160
        x = (self.sw - win_w) // 2
        y = (self.sh - win_h) // 2
        w.geometry(f"{win_w}x{win_h}+{x}+{y}")

        tk.Label(
            w, text=msg, bg="#FFF5F5", fg="#FF6B6B",
            font=('楷体', 14), wraplength=win_w - 50,
            justify="center",
        ).pack(expand=True)

        # 点击寄语窗口退出，点关闭按钮(X)也彻底退出
        def close_final():
            try:
                w.destroy()
            except Exception:
                pass
            self._do_exit()
        w.bind("<Button-1>", lambda e: close_final())
        w.protocol("WM_DELETE_WINDOW", close_final)


if __name__ == "__main__":
    HeartApp()
