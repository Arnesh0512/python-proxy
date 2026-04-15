from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import csv
from datetime import datetime
import smtplib
import random
import winreg

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "log.csv"

templates = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates"))
)

SENDER_EMAIL = "arnesh052006@gmail.com"
APP_PASSWORD = "tebm bcpa gvxf bamj"

otp_value = None


# -------- CSV --------

def write_log(state):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([state, datetime.now().isoformat()])


def get_state():
    try:
        with open(LOG_FILE, "r") as f:
            rows = list(csv.reader(f))
            return rows[-1][0] if rows else "unblocked"
    except:
        return "unblocked"


def unlocks_this_month():
    count = 0
    now = datetime.now()

    try:
        with open(LOG_FILE, "r") as f:
            for row in csv.reader(f):
                state, t = row
                dt = datetime.fromisoformat(t)

                if state == "unblocked" and dt.month == now.month and dt.year == now.year:
                    count += 1
    except:
        pass

    return count


# -------- REGISTRY --------

def block_settings():
    key = winreg.CreateKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
    )
    winreg.SetValueEx(key, "NoControlPanel", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)
    write_log("blocked")


def unblock_settings():
    key = winreg.CreateKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
    )
    winreg.SetValueEx(key, "NoControlPanel", 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
    write_log("unblocked")


# -------- ROUTES --------

@router.get("/settings", response_class=HTMLResponse)
def settings_page():
    template = templates.get_template("settings.html")
    return HTMLResponse(template.render(state=get_state()))


@router.get("/status")
def status():
    return {"state": get_state()}


@router.post("/toggle")
def toggle():
    state = get_state()

    if state == "unblocked":
        block_settings()
        return {"status": "blocked"}

    else:
        if unlocks_this_month() >= 2:
            return {"error": "Monthly unlock limit reached"}

        return {"status": "otp_required"}


@router.post("/send-otp")
def send_otp():
    global otp_value

    otp_value = random.randint(100000, 999999)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        msg = f"Subject: OTP\n\nYour OTP is {otp_value}"
        server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg)
        server.quit()

        return {"status": "sent"}

    except Exception as e:
        return {"error": str(e)}


@router.post("/verify-otp")
def verify_otp(data: dict):
    global otp_value

    try:
        user_otp = int(data.get("otp"))
    except:
        return {"error": "Invalid OTP"}

    if user_otp == otp_value:
        unblock_settings()
        return {"status": "unblocked"}

    return {"error": "Wrong OTP"}