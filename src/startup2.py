import os
import sys
import time
import socket
import getpass
import platform
import urllib.request
from datetime import datetime
import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Optional Windows Location API
try:
    from winsdk.windows.devices import geolocation as wdg
    import asyncio

    async def get_gps_location():
        locator = wdg.Geolocator()
        pos = await locator.get_geoposition_async()
        return {
            "lat": pos.coordinate.point.position.latitude,
            "lon": pos.coordinate.point.position.longitude,
            "accuracy": pos.coordinate.accuracy
        }

    HAS_WINSDK = True
except Exception:
    HAS_WINSDK = False

# Webcam capture (OpenCV)
try:
    import cv2
    HAS_OPENCV = True
except Exception:
    HAS_OPENCV = False

# ----------------- Logging setup -----------------
BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
log_path = os.path.join(BASE_DIR, "startup_error_log.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)

# ----------------- Environment variables -----------------
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    logging.error(f".env file not found at {env_path}")
    sys.exit(1)

SENDER = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
RECEIVER = os.getenv("EMAIL_RECEIVER")
if not all([SENDER, PASSWORD, RECEIVER]):
    logging.error("Missing EMAIL_USER, EMAIL_PASS, or EMAIL_RECEIVER in .env")
    sys.exit(1)

# Configurable SMTP (defaults to Gmail)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Webcam preference
ENABLE_WEBCAM = os.getenv("ENABLE_WEBCAM", "true").lower() == "true"

# ----------------- Internet check (with max retries) -----------------
def wait_for_internet(timeout=5, retry_interval=10, max_retries=30):
    """Wait for internet connectivity with a maximum retry limit."""
    for attempt in range(max_retries):
        try:
            urllib.request.urlopen("https://www.google.com", timeout=timeout)
            return True
        except Exception:
            logging.warning(
                "No internet... retrying in %ds (%d/%d)",
                retry_interval, attempt + 1, max_retries
            )
            time.sleep(retry_interval)
    logging.error("Max retries reached — no internet available. Giving up.")
    return False

# ----------------- System info -----------------
def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception:
        return "Unavailable"

def get_ip_location(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if res.get("status") == "success":
            return {
                "city": res.get("city"),
                "region": res.get("regionName"),
                "country": res.get("country"),
                "lat": res.get("lat"),
                "lon": res.get("lon"),
                "isp": res.get("isp"),
            }
    except Exception:
        return None
    return None

# ----------------- Webcam capture -----------------
def capture_webcam_photo(device_indices=(0, 1), width=1280, height=720, warmup_frames=5, read_timeout=5):
    """Capture a single frame from the webcam. Returns JPEG bytes or None."""
    if not ENABLE_WEBCAM:
        logging.info("Webcam capture disabled by user preference.")
        return None

    if not HAS_OPENCV:
        logging.warning("OpenCV not available; skipping webcam capture.")
        return None

    for dev in device_indices:
        cap = None
        try:
            cap = cv2.VideoCapture(dev, cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY)
            if not cap or not cap.isOpened():
                if cap:
                    cap.release()
                continue

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            for _ in range(warmup_frames):
                ret, frame = cap.read()
                if not ret:
                    break

            start = time.time()
            while time.time() - start < read_timeout:
                ret, frame = cap.read()
                if ret and frame is not None:
                    ret_enc, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    if ret_enc:
                        logging.info(f"Captured webcam image from device {dev}")
                        return buf.tobytes()
                    break
                time.sleep(0.1)
        except Exception as e:
            logging.warning(f"Error capturing from webcam device {dev}: {e}")
        finally:
            if cap:
                cap.release()

    logging.warning("No working webcam found or capture failed.")
    return None

# ----------------- Send email -----------------
def send_email():
    logging.info("Script started")

    if not wait_for_internet():
        logging.error("Aborting — no internet connection.")
        sys.exit(1)

    logging.info("Internet available, gathering info...")

    hostname = socket.gethostname() or "Unavailable"
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "Unavailable"

    public_ip = get_public_ip()
    username = getpass.getuser()
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
    machine_info = f"{platform.machine()} | {platform.processor()}"
    now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    # --- Location ---
    location_text = "Unavailable"
    maps_link = ""
    latitude = longitude = None

    if HAS_WINSDK:
        try:
            location = asyncio.run(asyncio.wait_for(get_gps_location(), timeout=10))
            latitude = location.get("lat")
            longitude = location.get("lon")
            accuracy = location.get("accuracy")
            location_text = f"Windows Location API (GPS/WiFi): {latitude}, {longitude} (±{accuracy}m)"
        except Exception as e:
            logging.warning(f"Windows location failed, using IP lookup: {e}")

    if latitude is None or longitude is None:
        loc = get_ip_location(public_ip)
        if loc:
            latitude = loc.get("lat")
            longitude = loc.get("lon")
            location_text = (
                f"IP-based Location: {loc['city']}, {loc['region']}, {loc['country']} "
                f"(Lat: {latitude}, Lon: {longitude}) | ISP: {loc['isp']}"
            )

    if latitude is not None and longitude is not None:
        maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
        location_text += f"\nGoogle Maps: {maps_link}"

    # --- Email content ---
    subject = f"System Report from {hostname}"
    body_text = f"""
Time: {now}
User: {username}
Hostname: {hostname}
Local IP: {local_ip}
Public IP: {public_ip}
OS: {os_info}
Machine: {machine_info}

Location:
{location_text}
"""

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = RECEIVER
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    img_bytes = capture_webcam_photo()
    if img_bytes:
        try:
            image_part = MIMEImage(img_bytes, _subtype="jpeg")
            image_part.add_header("Content-Disposition", 'attachment', filename="snapshot.jpg")
            msg.attach(image_part)
            logging.info("Webcam image attached to email.")
        except Exception as e:
            logging.warning(f"Failed to attach image: {e}")
    else:
        logging.info("No webcam image to attach.")

    try:
        logging.info(f"Connecting to SMTP server {SMTP_HOST}:{SMTP_PORT}...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, msg.as_string())
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
