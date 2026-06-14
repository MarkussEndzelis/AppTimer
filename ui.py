import tkinter as tk
from tkinter import ttk
import threading
import time
import tracker
import datetime
from PIL import Image, ImageTk

class AppTimerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AppTimer")
        self.root.geometry("600x600")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)
        self._build()
        self.icon_cache = {}
        self.icon_refs = []
        self._start_tracking()

    def _build(self):
        tk.Label(self.root, text="AppTimer", fg="white", bg="#1e1e2e", font=("Segoe UI", 20, "bold")).pack(pady=(20, 4))
        tk.Label(self.root, text="Running app durations", fg="#576574", bg="#1e1e2e", font=("Segoe UI", 10)).pack(pady=(0, 16))

        search_frame = tk.Frame(self.root, bg="#1e1e2e")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        tk.Label(search_frame, text="Search:", fg="#a0a0b0", bg="#1e1e2e", font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._refresh_table())
        tk.Entry(search_frame, textvariable=self.search_var, bg="#2f3542", fg="white", insertbackground="white", font=("Segoe UI", 10),
                 borderwidth=0).pack(side="left", fill="x", expand=True)
        
        self.show_all_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self.root, text="Show all processes", variable=self.show_all_var,
                       bg="#1e1e2e", fg="white", selectcolor="#2f3542",
                       font=("Segoe UI", 10),
                       command=self._force_refresh).pack(anchor="w", padx=20, pady=(0,8))
        
        cols = ("App", "Time Running", "Started")
        self.tree = ttk.Treeview(self.root, columns=cols, show="tree headings", style="Dark.Treeview")
        self.tree.column("#0", width=30)
        self.sort_col = "Time Running"
        self.sort_reverse = True
        self.tree.heading("App", text="App", command=lambda: self._sort_by("App"))
        self.tree.heading("Time Running", text="Time Running", command=lambda: self._sort_by("Time Running"))
        self.tree.heading("Started", text="Started", command=lambda: self._sort_by("Started"))
        self.tree.column("App", width=250)
        self.tree.column("Time Running", width=150)
        self.tree.column("Started", width=100)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.status_var = tk.StringVar(value="Loading...")
        tk.Label(self.root, textvariable=self.status_var, fg="#576574", bg="#1e1e2e", font=("Segoe UI", 9)).pack(pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview", background="#2f3542", foreground="white", fieldbackground="#2f3542", rowheight=28, font=("Segoe UI", 10))
        style.configure("Dark.Treeview.Heading", background="#1e1e2e", foreground="#a0a0b0", font=("Segoe UI", 10, "bold"))
        style.map("Dark.Treeview", background=[("selected", "#5865f2")])

    def _refresh_table(self):
        search = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        if self.sort_col == "App":
            apps = sorted(self.current_apps.items(), key=lambda x: x[0].lower(), reverse=self.sort_reverse)
        elif self.sort_col == "Started":
            apps = sorted(self.current_apps.items(), key=lambda x: x[1]["start"], reverse=self.sort_reverse)
        else:
            apps = sorted(self.current_apps.items(), key=lambda x: x[1]["time"], reverse=self.sort_reverse)
        for name, data in apps:
            if search and search not in name.lower():
                continue
            started = datetime.datetime.fromtimestamp(data["start"]).strftime("%I:%M %p")
            if name not in self.icon_cache:
                img = tracker.get_app_icon(name)
                if img:
                    photo = ImageTk.PhotoImage(img)
                    self.icon_cache[name] = photo
                    self.icon_refs.append(photo)
                else:
                    self.icon_cache[name] = None
            icon = self.icon_cache.get(name)
            if icon:
                self.tree.insert("", "end", image=icon, values=(name, tracker.format_time(data["time"]), started))
            else:
                self.tree.insert("", "end", values=(name, tracker.format_time(data["time"]), started))
        if self.current_apps:
            top_app = max(self.current_apps.items(), key=lambda x: x[1]["time"])
            top_name = top_app[0]
            self.status_var.set(f"{len(self.current_apps)} apps open - Most active: {top_name} ({tracker.format_time(top_app[1]['time'])})")
        else:
            self.status_var.set("No apps detected")

    def _force_refresh(self):
        self.current_apps = tracker.get_running_apps(self.show_all_var.get())
        self._refresh_table()    

    def _sort_by(self, col):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = col == "Time Running"
        self._refresh_table()

    def _start_tracking(self):
        self.current_apps = {}
        def loop():
            while True:
                self.current_apps = tracker.get_running_apps(self.show_all_var.get())
                self.root.after(0, self._refresh_table)
                time.sleep(3)
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def run(self):
        self.root.mainloop()
