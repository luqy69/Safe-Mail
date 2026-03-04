# SafeMail — Setup Guide

## What's inside
| File | Purpose |
|------|--------|
| `setup.exe` | Run this first to install SafeMail |
| `startup2.exe` | The background agent (auto-copied during setup) |
| `uninstall.exe` | Run this to completely remove SafeMail |

> Download the exe files from the [Releases page](../../releases/latest).

## How to Install

1. **Right-click `setup.exe`** → **Run as administrator**
2. Follow the prompts:
   - Enter your **Gmail address** (sender)
   - Enter your **Gmail App Password** (see below)
   - Enter the **recipient email address**
   - Choose whether to enable **webcam capture**
   - Enter your **Windows password** (for Task Scheduler)
3. Done! SafeMail will run silently every time you log in.

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
