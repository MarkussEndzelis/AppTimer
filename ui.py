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
        self.root.geometry("680x620")
        self.root.configure(bg="#13131f")
        self.root.resizable(True, True)
        self.icon_cache = {}
        self.icon_refs = []
        self._build()
        self._start_tracking()

    def _build(self):
        # Header
        header = tk.Frame(self.root, bg="#13131f")
        header.pack(fill="x", padx=30, pady=(28, 0))
        tk.Label(header, text="AppTimer", fg="white", bg="#13131f",
                 font=("Segoe UI", 24, "bold")).pack(side="left")
        self.status_var = tk.StringVar(value="Loading...")
        tk.Label(header, textvariable=self.status_var, fg="#404060",
                 bg="#13131f", font=("Segoe UI", 9)).pack(side="right", pady=(8, 0))

        tk.Label(self.root, text="Track how long your apps have been running",
                 fg="#404060", bg="#13131f",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=30, pady=(2, 20))

        # Search + toggle row
        row = tk.Frame(self.root, bg="#13131f")
        row.pack(fill="x", padx=30, pady=(0, 12))

        search_bg = tk.Frame(row, bg="#1e1e30", padx=10, pady=6)
        search_bg.pack(side="left", fill="x", expand=True)
        tk.Label(search_bg, text="🔍", bg="#1e1e30", fg="#404060",
                 font=("Segoe UI", 10)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._refresh_table())
        tk.Entry(search_bg, textvariable=self.search_var, bg="#1e1e30",
                 fg="white", insertbackground="white", font=("Segoe UI", 10),
                 borderwidth=0, highlightthickness=0).pack(side="left", fill="x",
                                                           expand=True, padx=(6, 0))

        self.show_all_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row, text="All processes", variable=self.show_all_var,
                       bg="#13131f", fg="#a0a0b0", selectcolor="#1e1e30",
                       activebackground="#13131f", activeforeground="white",
                       font=("Segoe UI", 10),
                       command=self._force_refresh).pack(side="right", padx=(12, 0))

        # Table
        table_frame = tk.Frame(self.root, bg="#1e1e30")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 0))

        cols = ("App", "Time Running", "Started")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="tree headings",
                                  style="Dark.Treeview")
        self.tree.column("#0", width=28, minwidth=28, stretch=False)
        self.sort_col = "Time Running"
        self.sort_reverse = True
        self.tree.heading("App", text="App", command=lambda: self._sort_by("App"))
        self.tree.heading("Time Running", text="Time Running",
                          command=lambda: self._sort_by("Time Running"))
        self.tree.heading("Started", text="Started",
                          command=lambda: self._sort_by("Started"))
        self.tree.column("App", width=260)
        self.tree.column("Time Running", width=160)
        self.tree.column("Started", width=110)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # Bottom bar
        bottom = tk.Frame(self.root, bg="#0f0f1a", pady=10)
        bottom.pack(fill="x", padx=0)
        tk.Label(bottom, text="Updates every 3 seconds", fg="#2a2a40",
                 bg="#0f0f1a", font=("Segoe UI", 8)).pack(side="right", padx=20)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview", background="#1e1e30", foreground="white",
                        fieldbackground="#1e1e30", rowheight=32,
                        font=("Segoe UI", 10), borderwidth=0)
        style.configure("Dark.Treeview.Heading", background="#13131f",
                        foreground="#606080", font=("Segoe UI", 9, "bold"),
                        borderwidth=0, relief="flat")
        style.map("Dark.Treeview", background=[("selected", "#2d2d50")])
        style.layout("Dark.Treeview", [('Dark.Treeview.treearea', {'sticky': 'nswe'})])

    def _refresh_table(self):
        search = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        if self.sort_col == "App":
            apps = sorted(self.current_apps.items(), key=lambda x: x[0].lower(),
                          reverse=self.sort_reverse)
        elif self.sort_col == "Started":
            apps = sorted(self.current_apps.items(), key=lambda x: x[1]["start"],
                          reverse=self.sort_reverse)
        else:
            apps = sorted(self.current_apps.items(), key=lambda x: x[1]["time"],
                          reverse=self.sort_reverse)
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
                self.tree.insert("", "end", image=icon,
                                 values=(name, tracker.format_time(data["time"]), started))
            else:
                self.tree.insert("", "end",
                                 values=(name, tracker.format_time(data["time"]), started))
        if self.current_apps:
            top_app = max(self.current_apps.items(), key=lambda x: x[1]["time"])
            top_name = top_app[0]
            self.status_var.set(
                f"{len(self.current_apps)} apps — top: {top_name} {tracker.format_time(top_app[1]['time'])}")
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