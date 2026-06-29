"""
Camera & Microphone Access Detection System
---------------------------------------------
Monitors Windows' built-in privacy registry (CapabilityAccessManager) to
detect when an application accesses the webcam or microphone, and sends
a WhatsApp alert if the accessing app isn't in the trusted list.

NOTE: Your phone number is no longer hardcoded here — set it as an
environment variable before running (see README for instructions):

    Windows (PowerShell):  $env:ALERT_PHONE_NUMBER="+91XXXXXXXXXX"
    Windows (cmd):         set ALERT_PHONE_NUMBER=+91XXXXXXXXXX
"""

import winreg
import time
import tkinter as tk
from threading import Thread
import os
import pywhatkit as kit

MY_PHONE_NUMBER = os.environ.get("ALERT_PHONE_NUMBER", "")
ALERT_COOLDOWN = 300  # seconds between repeat alerts

REG_PATHS = [
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam", "CAM"),
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone", "MIC")
]

# Apps in this list are considered "trusted" and won't trigger an alert
TRUSTED_KEYWORDS = ["GOOGLE", "CHROME", "ZOOM", "WHATSAPP", "FACEBOOK", "CAMERA", "MICROSOFT", "SKYPE", "TEAMS", "PYTHON"]


class SecurityWidget:
    def __init__(self):
        self.last_alert_time = 0
        self.root = tk.Tk()
        self.root.geometry("380x110")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.config(bg="#121212")

        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        self.main_frame = tk.Frame(self.root, bg="#1a1a1a", highlightbackground="#333", highlightthickness=2)
        self.main_frame.pack(fill="both", expand=True)

        self.status_label = tk.Label(self.main_frame, text="🛡️ SYSTEM SECURE",
                                      font=("Segoe UI", 12, "bold"), fg="#2ecc71", bg="#1a1a1a")
        self.status_label.pack(pady=(15, 2))

        self.app_info = tk.Label(self.main_frame, text="All Sensors: Idle",
                                  font=("Segoe UI", 10), fg="#888", bg="#1a1a1a")
        self.app_info.pack()

        self.close_btn = tk.Button(self.main_frame, text="✕", command=self.root.destroy,
                                    bg="#1a1a1a", fg="#555", bd=0, cursor="hand2")
        self.close_btn.place(x=355, y=5)

        if not MY_PHONE_NUMBER:
            print("⚠️  ALERT_PHONE_NUMBER environment variable not set — WhatsApp alerts disabled.")

        Thread(target=self.check_loop, daemon=True).start()
        self.root.mainloop()

    def start_move(self, event):
        self.x, self.y = event.x, event.y

    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def send_whatsapp_alert(self, app_details):
        """Sends an instant WhatsApp message when unauthorized access is found."""
        if not MY_PHONE_NUMBER:
            return
        current_time = time.time()
        if current_time - self.last_alert_time > ALERT_COOLDOWN:
            try:
                msg = f"🚨 SECURITY ALERT: Unauthorized {app_details} access detected on your PC!"
                kit.sendwhatmsg_instantly(MY_PHONE_NUMBER, msg, wait_time=15, tab_close=True)
                self.last_alert_time = current_time
            except Exception as e:
                print(f"WhatsApp Error: {e}")

    def get_display_name(self, raw_name):
        raw_upper = raw_name.upper()
        if "GOOGLE" in raw_upper or "CHROME" in raw_upper:
            return "CHROME"
        if "ZOOM" in raw_upper:
            return "ZOOM"
        if "WHATSAPP" in raw_upper:
            return "WHATSAPP"
        if "WINDOWSCAMERA" in raw_upper:
            return "CAMERA APP"
        return raw_name.split('#')[-1].upper()[:15]

    def check_loop(self):
        while True:
            active_info = []
            for hkey, base, sensor_type in REG_PATHS:
                for sub in [base, f"{base}\\NonPackaged"]:
                    try:
                        with winreg.OpenKey(hkey, sub) as key:
                            for i in range(winreg.QueryInfoKey(key)[0]):
                                name = winreg.EnumKey(key, i)
                                if name == "NonPackaged":
                                    continue
                                in_use = False
                                full_p = f"{sub}\\{name}"
                                with winreg.OpenKey(hkey, full_p) as k:
                                    try:
                                        stop, _ = winreg.QueryValueEx(k, "LastUsedTimeStop")
                                        if stop == 0:
                                            in_use = True
                                    except Exception:
                                        pass
                                    try:
                                        with winreg.OpenKey(hkey, f"{full_p}\\#") as sk:
                                            val, _ = winreg.QueryValueEx(sk, "Value")
                                            if val == "InUse":
                                                in_use = True
                                    except Exception:
                                        pass

                                if in_use:
                                    is_trusted = any(word in name.upper() for word in TRUSTED_KEYWORDS)
                                    active_info.append((sensor_type, self.get_display_name(name), is_trusted))
                    except Exception:
                        continue

            if active_info:
                danger_apps = [f"[{s}] {n}" for s, n, t in active_info if not t]
                display_parts = [f"[{s}] {n}" for s, n, t in active_info]
                unique_display = ", ".join(set(display_parts))

                if danger_apps:
                    self.status_label.config(text="🚨 UNAUTHORIZED ACCESS!", fg="#ff4757")
                    self.main_frame.config(highlightbackground="#ff4757")
                    self.app_info.config(text=unique_display, fg="white")

                    alert_details = ", ".join(set(danger_apps))
                    Thread(target=self.send_whatsapp_alert, args=(alert_details,), daemon=True).start()
                else:
                    self.status_label.config(text="📷 SENSOR ACTIVE", fg="#3498db")
                    self.main_frame.config(highlightbackground="#3498db")
                    self.app_info.config(text=unique_display, fg="white")
            else:
                self.status_label.config(text="🛡️ SYSTEM SECURE", fg="#2ecc71")
                self.app_info.config(text="All Sensors: Idle", fg="#888")
                self.main_frame.config(highlightbackground="#333")

            time.sleep(1)


if __name__ == "__main__":
    SecurityWidget()
