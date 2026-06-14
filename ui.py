import tkinter as tk
from tkinter import ttk
import threading
import time
import tracker

class AppTimerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AppTimer")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)
        self._build()
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
        
        cols = ("App", "Time Running")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", style="Dark.Treeview")
        self.tree.heading("App", text="App")
        self.tree.heading("Time Running", text="Time Running")
        self.tree.column("App", width=350)
        self.tree.column("Time Running", width=150)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.status_var = tk.StringVar(value="Loading...")
        tk.Label(self.root, textvariable=self.status_var, fg="#576574", bg="#1e1e2e", font=("Segoe UI", 9)).pack(pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview", background="#2f3542", foreground="white", fieldbackground="#2f3542", rowheight=28, font=("Segoe UI", 10))
        style.map("Dark.Treeview", background=[("selected", "#5865f2")])

    def _refresh_table(self):
        search = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        apps = sorted(self.current_apps.items(), key=lambda x: x[1], reverse=True)
        for name, seconds in apps:
            if search and search not in name.lower():
                continue
            self.tree.insert("", "end", values=(name, tracker.format_time(seconds)))
        self.status_var.set(f"Tracking {len(self.current_apps)} apps - updated just now")

    def _start_tracking(self):
        self.current_apps = {}
        def loop():
            while True:
                self.current_apps = tracker.get_running_apps()
                self.root.after(0, self._refresh_table)
                time.sleep(3)
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def run(self):
        self.root.mainloop()
