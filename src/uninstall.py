import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

# Import shared utilities
from utils import (
    run_as_admin, print_logo,
    USER_APPDATA, STARTUP_EXE, ENV_FILE, VBS_FILE, TASK_NAME,
)

# ===============================================
#  AUTO ELEVATE TO ADMIN
# ===============================================
run_as_admin()

# ===============================================
#  DISPLAY SAFE-MAIL LOGO
# ===============================================
print_logo(subtitle="SafeMail Uninstaller", subtitle_color=Fore.RED)

# ===============================================
#  CONFIRMATION PROMPT
# ===============================================
choice = input(Fore.YELLOW + "⚠ Are you sure you want to uninstall SafeMail? (y/n): ").strip().lower()
if choice not in ("y", "yes"):
    print(Fore.CYAN + "\nUninstallation cancelled.")
    sys.exit(0)

# ===============================================
#  REMOVE TASK SCHEDULER ENTRY
# ===============================================
print(Fore.CYAN + "\nRemoving Task Scheduler entry...")
try:
    subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        check=True
    )
    print(Fore.GREEN + f"[✔] Task '{TASK_NAME}' deleted successfully!")
except subprocess.CalledProcessError:
    print(Fore.YELLOW + f"[!] Task '{TASK_NAME}' not found or already deleted.")
time.sleep(0.5)

# ===============================================
#  DELETE FILES
# ===============================================
for file in [STARTUP_EXE, ENV_FILE, VBS_FILE]:
    if file.exists():
        try:
            file.unlink()
            print(Fore.GREEN + f"[✔] Deleted {file.name}")
        except Exception as e:
            print(Fore.RED + f"[✖] Failed to delete {file.name}: {e}")
    else:
        print(Fore.YELLOW + f"[!] {file.name} not found (already removed)")
time.sleep(0.5)

# ===============================================
#  DELETE SafeMail FOLDER IF EXISTS
# ===============================================
if USER_APPDATA.exists():
    try:
        shutil.rmtree(USER_APPDATA)
        print(Fore.GREEN + f"[✔] Removed folder: {USER_APPDATA}")
    except Exception as e:
        print(Fore.RED + f"[✖] Failed to remove folder: {e}")
else:
    print(Fore.YELLOW + f"[!] Folder not found: {USER_APPDATA}")
time.sleep(0.5)

# ===============================================
#  FINISH
# ===============================================
print(Fore.GREEN + "\n" + "═" * 50)
print(Fore.GREEN + "  Uninstallation completed successfully.")
print(Fore.GREEN + "═" * 50)
input("\nPress Enter to exit...")
