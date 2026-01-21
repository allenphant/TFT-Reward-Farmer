import pydirectinput
import keyboard
import random
import time
import ctypes
import pyautogui
import os
import tkinter as tk
from threading import Thread
from datetime import datetime

# --- 基礎設定 ---
PATH = r'C:\Your_Project_Path\assets'
IMG_EXIT = os.path.join(PATH, 'exit.png')
IMG_AGAIN = os.path.join(PATH, 'play_again.png')
IMG_FIND = os.path.join(PATH, 'find_match.png')
IMG_ACCEPT = os.path.join(PATH, 'accept.png')
IMG_LOBBY_UI = os.path.join(PATH, 'lobby_ui.png') 
IMG_QUICK_PLAY = os.path.join(PATH, 'quick_play.png')
IMG_SKIP = os.path.join(PATH, 'skip.png')
IMG_RECONNECT = os.path.join(PATH, 'reconnect.png')
IMG_IN_GAME_TITLE = os.path.join(PATH, 'in_game_title.png')
IMG_INGAME_ICON = os.path.join(PATH, 'ingame_icon.png')
IMG_CLIENT_ICON = os.path.join(PATH, 'client_icon.png')
IMG_CLIENT_YELLOW = os.path.join(PATH, 'client_icon_yellow.png')
IMG_NOW_GAMING = os.path.join(PATH, 'now_gaming.png')
# 新增：組隊房間圖示
IMG_PARTY_ROOM = os.path.join(PATH, 'party_room.png') 

pyautogui.FAILSAFE = False 
running = False

def get_now():
    return datetime.now().strftime("%H:%M:%S")

def log_msg(msg):
    print(f"[{get_now()}] {msg}", flush=True)

def show_toast(text, duration=1200):
    timestamp_text = f"[{get_now()}] {text}"
    def create_window():
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True, "-alpha", 0.8)
            label = tk.Label(root, text=timestamp_text, font=("Microsoft JhengHei", 12, "bold"), 
                             fg="white", bg="black", padx=15, pady=8)
            label.pack()
            root.update_idletasks()
            sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
            x = (sw // 2) - (root.winfo_width() // 2)
            y = sh - 180 
            root.geometry(f"+{x}+{y}")
            root.after(duration, root.destroy)
            root.mainloop()
        except: pass
    Thread(target=create_window, daemon=True).start()

def set_mouse_pos(x, y):
    ctypes.windll.user32.SetCursorPos(x, y)

def physical_click(button='left', hold=0.15):
    pydirectinput.mouseDown(button=button)
    time.sleep(hold)
    pydirectinput.mouseUp(button=button)

def toggle_status(e):
    global running
    running = not running
    log_msg("🚀 腳本啟動" if running else "⏹️ 腳本停止")
    show_toast("🚀 腳本啟動" if running else "⏹️ 腳本停止")

keyboard.on_press_key("space", toggle_status)

user32 = ctypes.windll.user32
sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def safe_locate(img_path, conf=0.8):
    if not os.path.exists(img_path): return None
    try: return pyautogui.locateOnScreen(img_path, confidence=conf)
    except: return None

def find_and_click(img_path, name, conf=0.8):
    res = safe_locate(img_path, conf=conf)
    if res:
        log_msg(f"🎯 偵測到：{name}，準備點擊")
        center = pyautogui.center(res)
        show_toast(f"🎯 點擊：{name}")
        set_mouse_pos(int(center.x), int(center.y))
        time.sleep(0.4) 
        physical_click('left', hold=0.15)
        return True
    return False

log_msg("--- 腳本準備就緒 (包含組隊房間偵測) ---")

try:
    while True:
        if running:
            is_lobby = safe_locate(IMG_LOBBY_UI, conf=0.7)
            is_ingame = safe_locate(IMG_IN_GAME_TITLE, conf=0.7)

            if is_lobby:
                # --- 大廳模式：處理進入房間與排隊 ---
                if safe_locate(IMG_NOW_GAMING, conf=0.8):
                    log_msg("🚨 大廳顯示對戰中，嘗試恢復視窗")
                    if find_and_click(IMG_INGAME_ICON, "工作列遊戲圖示"):
                        time.sleep(3)
                        continue
                
                # 優先檢查是否卡在結算或斷線
                find_and_click(IMG_SKIP, "跳過結算", conf=0.7)
                find_and_click(IMG_RECONNECT, "重新連接", conf=0.7)
                
                # 邏輯：看到組隊房間亮起就點擊進入準備狀態
                if not find_and_click(IMG_PARTY_ROOM, "組隊房間"):
                    if not find_and_click(IMG_QUICK_PLAY, "快打模式"):
                        if not find_and_click(IMG_AGAIN, "再來一場"):
                            if not find_and_click(IMG_FIND, "尋找對戰"):
                                find_and_click(IMG_ACCEPT, "接受對戰")
                time.sleep(2)
            
            elif is_ingame:
                # --- 遊戲中模式：每一步都進行安全偵測 ---
                if find_and_click(IMG_ACCEPT, "接受對戰"):
                    time.sleep(5)
                    continue

                if find_and_click(IMG_EXIT, "現在離開", conf=0.7):
                    time.sleep(6)
                    continue

                # 無特殊情況才執行隨機動作
                tx = random.randint(int(sw*0.25), int(sw*0.75))
                ty = random.randint(int(sh*0.6), int(sh*0.9))
                
                # log_msg(f"🎲 安全偵測完畢，執行隨機動作 (座標: {tx}, {ty})")
                set_mouse_pos(tx, ty)
                time.sleep(0.5)
                pydirectinput.press('e')
                physical_click('right', hold=0.1)
                
                for _ in range(3):
                    physical_click('left', hold=0.1)
                    time.sleep(0.05)
                time.sleep(1)
            
            else:
                # --- 救援模式：嘗試恢復焦點 ---
                log_msg("⚠️ 失去焦點，搜尋工作列圖示...")
                if not find_and_click(IMG_INGAME_ICON, "工作列遊戲圖示"):
                    if not find_and_click(IMG_CLIENT_ICON, "工作列大廳圖示"):
                        find_and_click(IMG_CLIENT_YELLOW, "工作列大廳圖示(黃)")
                time.sleep(3)
        else:
            time.sleep(0.2)
except KeyboardInterrupt:
    log_msg("程式結束")