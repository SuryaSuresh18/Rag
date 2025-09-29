# agents/email_agent.py
import smtplib
from email.mime.text import MIMEText
from config import EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

def send_email(subject: str, body: str,receiver):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = receiver

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    print("✅ Email sent successfully.")
