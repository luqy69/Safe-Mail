# SafeMail — Setup Guide

## ⚠️ Antivirus Warning (False Positive)

**Windows Defender may flag the `.exe` files as a threat.** This is a **false positive** caused by PyInstaller-packaged executables that access system info, webcam, and email — behaviors that heuristic scanners associate with malware.

The source code is fully open and available in the [`src/`](../src/) folder for review.

### How to Allow SafeMail in Windows Defender:

1. Open **Windows Security** → **Virus & threat protection**
2. Scroll down and click **Protection history**
3. Find the SafeMail detection and click **Actions** → **Allow on device**

**Or add an exclusion before extracting:**
1. Open **Windows Security** → **Virus & threat protection**
2. Click **Manage settings** under *Virus & threat protection settings*
3. Scroll to **Exclusions** → **Add or remove exclusions**
4. Click **Add an exclusion** → **Folder** → select the SafeMail-Package folder

---

## What's inside
| File | Purpose |
|------|--------|
| `setup.exe` | Run this first to install SafeMail |
| `startup2.exe` | The background agent (auto-copied during setup) |
| `uninstall.exe` | Run this to completely remove SafeMail |

## How to Install

1. **Add the folder as a Defender exclusion** (see above)
2. **Right-click `setup.exe`** → **Run as administrator**
3. Follow the prompts:
   - Enter your **Gmail address** (sender)
   - Enter your **Gmail App Password** (see below)
   - Enter the **recipient email address**
   - Choose whether to enable **webcam capture**
   - Enter your **Windows password** (for Task Scheduler)
4. Done! SafeMail will run silently every time you log in.

## Getting a Gmail App Password

1. Go to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Select **Mail** and your device
3. Click **Generate**
4. Copy the **16-character password** — use this during setup

> ⚠️ Do NOT use your regular Gmail password. It will not work.

## How to Uninstall

1. **Right-click `uninstall.exe`** → **Run as administrator**
2. Confirm with `y`
3. Everything is cleaned up automatically

## Requirements
- Windows 10/11
- No Python needed — everything is bundled!
