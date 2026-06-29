# 🛡️ Camera & Microphone Access Detection System

A lightweight Windows desktop tool that monitors camera/microphone access
in real time and sends a WhatsApp alert when an untrusted application uses
either sensor.

## 🚀 Overview
Windows keeps a built-in privacy log (`CapabilityAccessManager`) of every
app that has accessed the camera or microphone. This tool reads that log
continuously, checks each accessing app against a trusted list, and shows
a small always-on-top floating widget with live status. If an app **not**
on the trusted list accesses the camera/mic, the widget turns red and an
instant WhatsApp alert is sent.

**Testing note:** During development, Chrome was deliberately treated as
an "untrusted" app to simulate and verify the alert flow end-to-end,
since it's an easy, repeatable way to trigger camera access. In normal
use, Chrome is trusted by default — only genuinely unrecognized apps
trigger an alert.

## 🛠️ Tech Stack
- Python
- `tkinter` (floating always-on-top status widget)
- `pywhatkit` (automated WhatsApp alerts)
- Windows Registry (`winreg`) — reads the built-in privacy/consent log

⚠️ **Platform note:** This tool is Windows-only, since it directly reads
Windows' `CapabilityAccessManager` registry keys.

## ✨ Key Features
- Real-time detection of camera/microphone access via Windows' own privacy log
- Always-on-top draggable widget showing live status (Secure / Active / Unauthorized)
- Trusted-app allowlist (Zoom, Teams, Skype, etc.) to avoid false alarms
- Automatic WhatsApp alert when an untrusted app is detected
- Alert cooldown to prevent spam from repeated triggers

## 🔌 How It Works
1. A background thread polls Windows' webcam/microphone consent registry keys every second.
2. For each active access, it checks the app name against a trusted keyword list.
3. If the app is trusted → widget shows "Sensor Active" (blue).
4. If the app is **not** trusted → widget shows "Unauthorized Access!" (red) and a WhatsApp alert is sent (rate-limited via cooldown).
5. If no access is detected → widget shows "System Secure" (green).

## ⚙️ Setup
1. Install dependencies:
   ```
   pip install pywhatkit
   ```
2. Set your phone number as an environment variable (your number is **not** hardcoded in the code, for privacy):
   ```
   # Windows PowerShell
   $env:ALERT_PHONE_NUMBER="+91XXXXXXXXXX"

   # Windows cmd
   set ALERT_PHONE_NUMBER=+91XXXXXXXXXX
   ```
3. Run:
   ```
   python camera_mic_monitor.py
   ```
4. Keep WhatsApp Web logged in in your default browser — `pywhatkit` sends messages through it.

## 📷 Demo
*(Add a screenshot/recording here showing the widget detecting Chrome's
webcam access and the resulting WhatsApp alert)*

## 📈 Planned Future Enhancements
- **IP-based remote access detection** — identify and flag access attempts
  originating from a different/unauthorized IP address (true network-level
  intrusion detection), to complement this local access-monitoring approach
- Persistent, user-editable trusted/blocked app list (currently hardcoded)
- Activity log with timestamps for reviewing past access events
- Cross-platform support (macOS/Linux currently unsupported — Windows registry-specific)

## 📌 Status
Local camera/mic access detection with WhatsApp alerting implemented and
tested on Windows (using Chrome as the test trigger). IP-based remote
intrusion detection is a planned future extension, not yet implemented.
