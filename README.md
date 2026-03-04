# 🔒 Safe-Mail

**A lightweight Windows startup monitoring tool** that silently sends system reports via email every time a user logs in. Designed for personal device security and tracking.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📥 Download

> **[⬇️ Download SafeMail-Package-v2.0.zip](../../releases/download/v2.0/SafeMail-Package-v2.0.zip)** — No Python needed, just extract and run!
>
> Or visit the [Releases page](../../releases/latest) to see all downloads.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **System Report** | Hostname, username, OS version, machine info |
| 🌐 **IP Tracking** | Local IP + public IP address |
| 📍 **Location** | GPS/WiFi via Windows Location API, with IP-based fallback + Google Maps link |
| 📷 **Webcam Snapshot** | Optional photo capture attached to the email |
| 🔕 **Silent Operation** | Runs invisibly via Task Scheduler + VBS wrapper |
| 🔧 **Easy Setup** | Guided CLI installer with input validation |
| 🗑️ **Clean Uninstall** | One-click removal of all files and scheduled tasks |
| 🔑 **Configurable SMTP** | Gmail by default, but works with any SMTP provider |
| 🔁 **Password Retry** | Up to 3 attempts if Windows password is entered incorrectly |

---

## 📋 Prerequisites

- **Windows 10/11**
- **Python 3.8+** (for development) — or use the pre-built `.exe` releases
- A **Gmail account** with an [App Password](https://myaccount.google.com/apppasswords)

---

## 🚀 Quick Start

### Option 1: Pre-built Executables (No Python needed)

1. Download the latest release from [Releases](../../releases)
2. Extract the zip
3. Right-click `setup.exe` → **Run as administrator**
4. Follow the guided prompts
5. Done! SafeMail runs silently at every login

### Option 2: Run from Source

```bash
git clone https://github.com/luqy69/Safe-Mail.git
cd Safe-Mail
pip install -r requirements.txt
cd src
python setup.py
```

---

## 🛠️ Setup Walkthrough

During setup you will be prompted for:

| Prompt | Description |
|--------|-------------|
| `EMAIL_USER` | Your Gmail address (sender) |
| `EMAIL_PASS` | Gmail **App Password** (16-char, NOT your login password) |
| `EMAIL_RECEIVER` | Recipient email address |
| `Webcam capture` | Enable or disable webcam snapshots (opt-in) |
| `SMTP settings` | Custom SMTP host/port (press Enter for Gmail defaults) |
| `Windows password` | Required for Task Scheduler — with retry on failure |

### Getting a Gmail App Password

1. Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and your device
3. Click **Generate**
4. Copy the **16-character password** — use this during setup

> ⚠️ **Do NOT use your regular Gmail password.** Gmail blocks sign-ins from third-party apps unless you use an App Password.

---

## 🗑️ Uninstalling

```bash
cd src
python uninstall.py
```

Or run `uninstall.exe` as Administrator. This removes:
- The Task Scheduler entry
- The `.env` file, VBS wrapper, and startup executable
- The entire `%APPDATA%\SafeMail` folder

---

## 📁 Project Structure

```
Safe-Mail/
├── src/                    # Source code
│   ├── utils.py            # Shared utilities (admin elevation, logo, input helpers)
│   ├── setup.py            # Installer — guided setup with validation
│   ├── startup2.py         # Core agent — runs at login, sends email report
│   └── uninstall.py        # Clean uninstaller
├── specs/                  # PyInstaller build specifications
│   ├── setup.spec
│   ├── startup2.spec
│   └── uninstall.spec
├── package/                # Download instructions for pre-built releases
├── .env.example            # Template for environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔨 Building Executables

```bash
pip install pyinstaller
cd specs
pyinstaller setup.spec --noconfirm
pyinstaller startup2.spec --noconfirm
pyinstaller uninstall.spec --noconfirm
```

Built executables will appear in the `dist/` folder.

---

## ⚙️ How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  setup.exe  │────>│  Task        │────>│  startup2.exe   │
│  (one-time) │     │  Scheduler   │     │  (runs at login)│
│             │     │  (LogonTask) │     │                 │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                                    ┌─────────────┴──────────────┐
                                    │  Gathers system info:      │
                                    │  • IP addresses            │
                                    │  • GPS/WiFi location       │
                                    │  • Webcam snapshot (opt.)  │
                                    │  • OS & machine details    │
                                    └─────────────┬──────────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  Sends email    │
                                         │  via SMTP/TLS   │
                                         └─────────────────┘
```

---

## 📄 License

This project is for **educational and personal security use only**.

---

*Made with ❤️ by [Luqy](https://github.com/luqy69)*
