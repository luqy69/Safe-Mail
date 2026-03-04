import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

# Import shared utilities
from utils import (
    run_as_admin, print_logo,
    get_password_masked, get_password_with_reveal, get_validated_email,
    USER_APPDATA, STARTUP_EXE, ENV_FILE, VBS_FILE, TASK_NAME,
)

# ===============================================
#  AUTO ELEVATE TO ADMIN
# ===============================================
run_as_admin()

# ===============================================
#  DISPLAY SAFE-MAIL LOGO
# ===============================================
print_logo(subtitle="Program Made By Luqy")

# ===============================================
#  CREATE APPDATA FOLDER
# ===============================================
USER_APPDATA.mkdir(parents=True, exist_ok=True)

# ===============================================
#  COPY startup2.exe TO APPDATA
# ===============================================
CURRENT_EXE = Path(__file__).parent / "startup2.exe"
if CURRENT_EXE.exists():
    try:
        shutil.copy2(CURRENT_EXE, STARTUP_EXE)
        print(Fore.GREEN + f"[✔] Copied startup2.exe to {STARTUP_EXE}")
    except Exception as e:
        print(Fore.RED + f"[✖] Failed to copy startup2.exe: {e}")
        sys.exit(1)
else:
    print(Fore.RED + "[✖] startup2.exe not found in the current folder.")
    sys.exit(1)
time.sleep(0.5)

# ===============================================
#  PROMPT USER FOR .ENV DETAILS (validated + masked)
# ===============================================
print(Fore.MAGENTA + "\nEnter your email details:")

# --- App Password guidance ---
print(Fore.YELLOW + """
┌─────────────────────────────────────────────────────────┐
│  IMPORTANT: Gmail requires an App Password.             │
│                                                         │
│  1. Go to https://myaccount.google.com/apppasswords     │
│  2. Select 'Mail' and your device                       │
│  3. Click 'Generate' and copy the 16-char password      │
│  4. Use that App Password below (NOT your Gmail login)  │
└─────────────────────────────────────────────────────────┘
""")

email_user = get_validated_email("EMAIL_USER (sender email): ")
email_pass = get_password_with_reveal("EMAIL_PASS (App Password): ")
email_receiver = get_validated_email("EMAIL_RECEIVER (recipient email): ")

# ===============================================
#  WEBCAM CONSENT (opt-in)
# ===============================================
print(Fore.YELLOW + "\n[!] SafeMail can capture a webcam photo each time it runs at login.")
print(Fore.YELLOW + "    The photo will be attached to the system report email.")
webcam_choice = input(Fore.CYAN + "Enable webcam capture? (y/n): ").strip().lower()
enable_webcam = "true" if webcam_choice in ("y", "yes") else "false"

# ===============================================
#  SMTP CONFIGURATION (optional, defaults to Gmail)
# ===============================================
print(Fore.CYAN + "\nSMTP Configuration (press Enter to use Gmail defaults):")
smtp_host = input("SMTP_HOST [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
smtp_port = input("SMTP_PORT [587]: ").strip() or "587"

# ===============================================
#  SAVE .ENV FILE
# ===============================================
with ENV_FILE.open("w") as f:
    f.write(f"EMAIL_USER={email_user}\n")
    f.write(f"EMAIL_PASS={email_pass}\n")
    f.write(f"EMAIL_RECEIVER={email_receiver}\n")
    f.write(f"SMTP_HOST={smtp_host}\n")
    f.write(f"SMTP_PORT={smtp_port}\n")
    f.write(f"ENABLE_WEBCAM={enable_webcam}\n")
print(Fore.GREEN + f"[✔] .env file created at {ENV_FILE}")
time.sleep(0.5)

# ===============================================
#  CREATE VBS WRAPPER
# ===============================================
vbs_content = f'CreateObject("Wscript.Shell").Run """{STARTUP_EXE}""", 0, False'
with VBS_FILE.open("w") as f:
    f.write(vbs_content)
print(Fore.GREEN + f"[✔] VBScript created at {VBS_FILE}")
time.sleep(0.5)

# ===============================================
#  PROMPT FOR WINDOWS PASSWORD (uses current username)
#  + TASK SCHEDULER CREATION (with retry on wrong password)
# ===============================================
try:
    prompt_user = os.getlogin()
except Exception:
    prompt_user = os.environ.get("USERNAME", "")

print(Fore.CYAN + f"\nTo enable 'Run whether user is logged on or not', the script needs")
print(Fore.CYAN + f"to store credentials for the account: {Fore.WHITE}{prompt_user}")

task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{prompt_user}</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>wscript.exe</Command>
      <Arguments>"{VBS_FILE}"</Arguments>
    </Exec>
  </Actions>
</Task>
"""

MAX_PASSWORD_ATTEMPTS = 3
task_created = False

for attempt in range(1, MAX_PASSWORD_ATTEMPTS + 1):
    prompt_pass = get_password_with_reveal(f"Windows password for {prompt_user}: ")

    print(Fore.CYAN + "\nCreating Task Scheduler task with full settings...")

    temp_xml = USER_APPDATA / "task_def.xml"
    with open(temp_xml, "w", encoding="utf-16") as f:
        f.write(task_xml)

    create_cmd = [
        "schtasks",
        "/Create",
        "/TN", TASK_NAME,
        "/F",
        "/XML", str(temp_xml),
        "/RU", prompt_user,
        "/RP", prompt_pass
    ]

    try:
        subprocess.run(create_cmd, check=True, shell=False)
        print(Fore.GREEN + f"[✔] Task '{TASK_NAME}' created successfully!")
        task_created = True
        break
    except subprocess.CalledProcessError:
        print(Fore.RED + f"\n[✖] Wrong password or insufficient privileges. (Attempt {attempt}/{MAX_PASSWORD_ATTEMPTS})")
        if attempt < MAX_PASSWORD_ATTEMPTS:
            retry = input(Fore.YELLOW + "Would you like to re-enter your password? (y/n): ").strip().lower()
            if retry not in ("y", "yes"):
                print(Fore.YELLOW + "Skipping Task Scheduler setup. You can re-run setup later.")
                break
        else:
            print(Fore.RED + f"[✖] Maximum attempts reached ({MAX_PASSWORD_ATTEMPTS}).")
            print(Fore.YELLOW + "Task Scheduler was NOT configured. You can re-run setup.exe to try again.")
    finally:
        try:
            temp_xml.unlink()
        except Exception:
            pass

# ===============================================
#  FINISH
# ===============================================
print(Fore.GREEN + "\n" + "═" * 50)
print(Fore.GREEN + "  Setup completed successfully!")
print(Fore.GREEN + "  SafeMail will now run silently at each login.")
print(Fore.GREEN + "═" * 50)
input("\nPress Enter to exit...")
