import requests
import os
import time
import ctypes
import threading
import sys
from PIL import Image
import pystray

# ----------------------------------------------------
# 固定输出路径：在 EXE 同目录
# ----------------------------------------------------
# 【重要修改 1】：确保 BASE_DIR 始终指向 EXE 所在的目录（解决文件生成位置问题）
if getattr(sys, 'frozen', False):
    # 当作为 PyInstaller 打包的 EXE 运行时，使用 EXE 文件所在的目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 当作为普通 Python 脚本运行时，使用脚本所在目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_FILE = os.path.join(BASE_DIR, "earth_latest.jpg")
WALLPAPER_FILE = os.path.join(BASE_DIR, "wallpaper.jpg")
LOG_FILE = os.path.join(BASE_DIR, "log.txt")

API_URL = "https://earth.loadream.com/api.php"
UPDATE_INTERVAL = 15 * 60  # 15分钟


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)


# ----------------------------------------------------
# 获取最新图片 (无变化)
# ----------------------------------------------------
def download_latest_image():
    try:
        log("[INFO] 请求 API 获取最新图片 URL...")
        resp = requests.get(API_URL, timeout=10)
        resp.raise_for_status()

        img_url = None
        try:
            j = resp.json()
            for key in ("latest_url", "url", "image", "latest"):
                if isinstance(j, dict) and key in j and j[key]:
                    img_url = j[key]
                    break
            if not img_url and isinstance(j, str) and j.strip():
                img_url = j.strip()
        except ValueError:
            txt = resp.text.strip()
            if txt:
                img_url = txt

        if not img_url:
            log("[ERROR] 未从 API 获得图片 URL")
            return None

        log(f"[INFO] 最新图片 URL: {img_url}")

        # 下载图片内容
        log("[INFO] 开始下载图片...")
        img_resp = requests.get(img_url, timeout=20)
        img_resp.raise_for_status()
        with open(SAVE_FILE, "wb") as f:
            f.write(img_resp.content)

        log(f"[INFO] 图片下载完成: {SAVE_FILE}")
        return SAVE_FILE

    except Exception as e:
        log(f"[ERROR] 下载失败: {e}")
        return None


# ----------------------------------------------------
# 制作壁纸（居中 + 黑色填充） (无变化)
# ----------------------------------------------------
def make_wallpaper(input_path):
    try:
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)

        log(f"[INFO] 屏幕分辨率: {sw}x{sh}")

        img = Image.open(input_path)
        iw, ih = img.size

        ratio = min(sw / iw, sh / ih)
        nw = int(iw * ratio)
        nh = int(ih * ratio)
        img = img.resize((nw, nh), Image.LANCZOS)

        canvas = Image.new("RGB", (sw, sh), "black")
        x = (sw - nw) // 2
        y = (sh - nh) // 2
        canvas.paste(img, (x, y))

        canvas.save(WALLPAPER_FILE)
        log("[INFO] 壁纸生成完成")
        return WALLPAPER_FILE

    except Exception as e:
        log(f"[ERROR] 壁纸生成失败: {e}")
        return None


# ----------------------------------------------------
# 设置为壁纸 (无变化)
# ----------------------------------------------------
def set_wallpaper(path):
    try:
        abs_path = os.path.abspath(path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
        log("[INFO] 壁纸设置成功")
    except Exception as e:
        log(f"[ERROR] 设置壁纸失败: {e}")


# ----------------------------------------------------
# 自动循环更新 (无变化)
# ----------------------------------------------------
def auto_update():
    while True:
        log("\n========== 更新开始 ==========")
        img_path = download_latest_image()
        if img_path:
            wp = make_wallpaper(img_path)
            if wp:
                set_wallpaper(wp)
        log("========== 更新结束 ==========\n")
        time.sleep(UPDATE_INTERVAL)


# ----------------------------------------------------
# 托盘图标（【重要修改 2】：改为加载 icon.ico 文件）
# ----------------------------------------------------
def load_custom_icon(size=(64, 64)):
    # PyInstaller 标准做法：访问通过 --add-data 打包进来的资源
    if getattr(sys, 'frozen', False):
        # 当作为 EXE 运行时，在临时目录 (sys._MEIPASS) 中查找 icon.ico
        icon_path = os.path.join(sys._MEIPASS, "icon.ico")
    else:
        # 脚本模式下在当前目录查找
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

    try:
        # 使用 Pillow 加载 icon.ico
        pil_image = Image.open(icon_path)
        pil_image = pil_image.resize(size, Image.LANCZOS)
        return pil_image
    except Exception as e:
        # 回退为黑色图标 (现在会记录警告)
        log(f"[WARN] 托盘图标加载失败 ({e})，使用黑色图标。请确保 icon.ico 与脚本一同打包。")
        return Image.new("RGBA", size, (0, 0, 0, 255))


def tray():
    # 替换原来的 load_python_icon()
    icon_image = load_custom_icon()

    def on_exit(icon, item):
        log("[INFO] 用户退出程序")
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(pystray.MenuItem("退出", on_exit))
    icon = pystray.Icon("Himawari8", icon_image, "Himawari 8 Wallpaper", menu)
    icon.run()


# ----------------------------------------------------
# 主程序入口 (无变化)
# ----------------------------------------------------
if __name__ == "__main__":
    log("程序启动")
    threading.Thread(target=auto_update, daemon=True).start()
    tray()