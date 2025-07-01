"""📞 EmergencyCallerBot
Detects user inactivity (> MAX_IDLE_SECONDS) and sends alert call / email.
"""
import os
import time
import threading
from typing import Optional
from email.message import EmailMessage
import smtplib
import ssl

MAX_IDLE = int(os.getenv("MAX_IDLE_SECONDS", 10800))  # 3h
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMERGENCY_PHONE = os.getenv("EMERGENCY_PHONE", "")

class EmergencyCallerBot:
    status = "ready"
    capabilities = ["offline_monitor", "alert_call"]

    def __init__(self):
        self.last_active = time.time()
        self._start_watchdog()

    def heartbeat(self):
        self.last_active = time.time()

    # --------------------------------------------------
    def _start_watchdog(self):
        t = threading.Thread(target=self._watch_loop, daemon=True)
        t.start()

    def _watch_loop(self):
        while True:
            if time.time() - self.last_active > MAX_IDLE:
                self.alert()
                self.last_active = time.time()
            time.sleep(60)

    # --------------------------------------------------
    def alert(self):
        msg = "Agentic system offline >3h. Please verify identity."
        print("[EmergencyCaller] ALERT:", msg)
        self._send_email(msg)
        # TODO: integrate voice call API (Twilio, etc.)

    def _send_email(self, body: str):
        if not (SMTP_SERVER and SMTP_USERNAME and SMTP_PASSWORD):
            return
        email = EmailMessage()
        email["From"] = SMTP_USERNAME
        email["To"] = SMTP_USERNAME
        email["Subject"] = "[Emergency] Dhaher AI Ecosystem"
        email.set_content(body)
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls(context=ctx)
            s.login(SMTP_USERNAME, SMTP_PASSWORD)
            s.send_message(email)


def emergency_caller_agent():
    return EmergencyCallerBot()