import psutil
import time
import json
import os
import sys
from datetime import date

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "data.json")

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"sessions": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)
    
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_running_apps(show_all=False):
    BLOCKED = {
    "explorer.exe", "TextInputHost.exe", "ApplicationFrameHost.exe",
    "SystemSettings.exe", "SearchHost.exe", "StartMenuExperienceHost.exe",
    "ShellExperienceHost.exe", "LockApp.exe", "LogiOverlay.exe",
    "NVIDIA Overlay.exe", "NvContainer.exe", "nvsphelper64.exe",
    "svchost.exe", "RuntimeBroker.exe", "dllhost.exe", "conhost.exe",
    "WmiPrvSE.exe", "SearchIndexer.exe", "taskhostw.exe",
    "msedgewebview2.exe", "WidgetBoard.exe"
}

    import win32gui
    import win32process

    visible_pids = set()

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            visible_pids.add(pid)

    win32gui.EnumWindows(callback, None)

    apps = {}
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            if not show_all and proc.info['pid'] not in visible_pids:
                continue
            name = proc.info['name']
            if not show_all and name in BLOCKED:
                continue
            name = name.replace(".exe", "")
            elapsed = time.time() - proc.info['create_time']
            create_time = proc.info['create_time']
            if name not in apps or elapsed > apps[name]["time"]:
                apps[name] = {"time": elapsed, "start": create_time}
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return apps

def format_time(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"
    
def get_app_icon(exe_name):
    try:
        import win32api
        import win32con
        import win32gui
        import win32ui
        from PIL import Image

        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] and proc.info['name'].lower().replace(".exe", "") == exe_name.lower():
                    exe_path = proc.info['exe']
                    if not exe_path:
                        return None
                    large, small = win32gui.ExtractIconEx(exe_path, 0)
                    if not large and not small:
                        return None
                    icon = large[0] if large else small[0]
                    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                    hbmp = win32ui.CreateBitmap()
                    hbmp.CreateCompatibleBitmap(hdc, 16, 16)
                    hdc2 = hdc.CreateCompatibleDC()
                    hdc2.SelectObject(hbmp)
                    win32gui.DrawIconEx(hdc2.GetHandleOutput(), 0, 0, icon, 16, 16, 0, None, win32con.DI_NORMAL)
                    bmp_info = hbmp.GetInfo()
                    bmp_str = hbmp.GetBitmapBits(True)
                    img = Image.frombuffer('RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'BGRX', 0, 1)
                    win32gui.DestroyIcon(icon)
                    return img
            except:
                continue
    except:
        pass
    return None