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

def get_running_apps():
    apps = {}
    for proc in psutil.process_iter(['name', 'create_time']):
        try:
            name = proc.info['name']
            create_time = proc.info['create_time']
            elapsed = time.time() - create_time
            if name not in apps:
                apps[name] = elapsed
            else:
                if elapsed > apps[name]:
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