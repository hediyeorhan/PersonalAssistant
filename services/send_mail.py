import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

def send_gmail(subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = os.getenv("mail_username")
    password = os.getenv("mail_password")

    from_email = username
    to_email = os.getenv("to_email")

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("✅ Mail gönderildi.")
    except Exception as e:
        print("❌ Mail gönderilemedi:", e)
