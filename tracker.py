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
            if name not in apps or elapsed > apps[name]:
                apps[name] = elapsed
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