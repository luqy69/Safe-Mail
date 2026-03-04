import os
import sys
import time
import ctypes
from pathlib import Path
from colorama import Fore, init
import msvcrt
import re

init(autoreset=True)

# ===============================================
#  SHARED PATHS
# ===============================================
USER_APPDATA = Path(os.getenv("APPDATA")) / "SafeMail"
STARTUP_EXE = USER_APPDATA / "startup2.exe"
ENV_FILE = USER_APPDATA / ".env"
VBS_FILE = USER_APPDATA / "launch_startup.vbs"
TASK_NAME = "SafeMailStartupTask"

# ===============================================
#  SAFE-MAIL LOGO
# ===============================================
LOGO = f"""{Fore.CYAN}
███████╗ █████╗ ███████╗███████╗    ███╗   ███╗ █████╗ ██╗██╗     
██╔════╝██╔══██╗██╔════╝██╔════╝    ████╗ ████║██╔══██╗██║██║     
███████╗███████║█████╗  █████╗█████╗██╔████╔██║███████║██║██║     
╚════██║██╔══██║██╔══╝  ██╔══╝╚════╝██║╚██╔╝██║██╔══██║██║██║     
███████║██║  ██║██║     ███████╗    ██║ ╚═╝ ██║██║  ██║██║███████╗
╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝"""


def print_logo(subtitle="Program Made By Luqy", subtitle_color=Fore.MAGENTA):
    """Print the Safe-Mail ASCII logo with a subtitle."""
    print(LOGO)
    print(subtitle_color + f"                 {subtitle}\n")
    time.sleep(1)


# ===============================================
#  AUTO ELEVATE TO ADMIN
# ===============================================
def run_as_admin():
    """Re-run the script as administrator if not elevated."""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except Exception:
        pass

    print(Fore.YELLOW + "\n[!] Requesting administrator privileges...")
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"[✖] Failed to elevate privileges: {e}")
        sys.exit(1)


# ===============================================
#  MASKED PASSWORD INPUT (shows '*' while typing)
#  Windows-only (uses msvcrt)
# ===============================================
def get_password_masked(prompt="Password: "):
    """
    Read a password from the console showing '*' for each character.
    Returns the entered string (without newline).
    """
    sys.stdout.write(prompt)
    sys.stdout.flush()
    buf = []
    while True:
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            sys.stdout.write("\n")
            return "".join(buf)
        if ch == "\x03":  # Ctrl-C
            raise KeyboardInterrupt
        if ch == "\x08":  # Backspace
            if buf:
                buf.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue
        buf.append(ch)
        sys.stdout.write("*")
        sys.stdout.flush()


def get_password_with_reveal(prompt="Password: "):
    """
    Read a masked password, then offer to reveal it for verification.
    Returns the confirmed password string.
    """
    while True:
        password = get_password_masked(prompt)
        if not password:
            print(Fore.RED + "Password cannot be empty. Try again.")
            continue

        choice = input(Fore.YELLOW + "Show password to verify? (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            print(Fore.WHITE + f"Your password: {password}")

        confirm = input(Fore.YELLOW + "Is this correct? (y/n): ").strip().lower()
        if confirm in ("y", "yes"):
            return password
        print(Fore.CYAN + "Let's try again.\n")


# ===============================================
#  EMAIL VALIDATION
# ===============================================
EMAIL_REGEX = re.compile(r'^[\w.\+\-]+@[\w\-]+\.[\w.\-]+$')


def get_validated_email(prompt="Email: "):
    """Prompt for an email address and validate its format."""
    while True:
        email = input(prompt).strip()
        if EMAIL_REGEX.match(email):
            return email
        print(Fore.RED + "Invalid email format. Please try again.")
