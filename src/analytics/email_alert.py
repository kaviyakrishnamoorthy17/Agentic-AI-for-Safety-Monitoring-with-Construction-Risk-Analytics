import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

SENDER_EMAIL = "kaviyakproject17@gmail.com"
APP_PASSWORD = "ggzebsfsboiigwsw"
RECEIVER_EMAIL = "kaviyakproject17@gmail.com"

# Only send an email for the same violation type once every 60 seconds
EMAIL_COOLDOWN_SECONDS = 60
last_email_time = {}


def send_alert_email(violation_type, severity, detected_at):
    now = datetime.now()

    if violation_type in last_email_time:
        time_since_last = now - last_email_time[violation_type]
        if time_since_last < timedelta(seconds=EMAIL_COOLDOWN_SECONDS):
            print(f"[EMAIL SKIPPED] {violation_type} still in cooldown")
            return

    subject = f"Safety Alert: {violation_type}"
    body = f"""
A safety violation was detected on the construction site.

Violation Type: {violation_type}
Severity: {severity}
Detected At: {detected_at}

Please take appropriate action.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        last_email_time[violation_type] = now
        print(f"[EMAIL SENT] Alert for {violation_type}")
    except Exception as e:
        print(f"[EMAIL FAILED] Could not send alert: {e}")