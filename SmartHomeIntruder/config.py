import smtplib
from email.message import EmailMessage
from pathlib import Path

# -------------------------
#  YOUR EMAIL SETTINGS
# -------------------------
EMAIL_FROM = "nandaprasad2004nanduzzz@gmail.com"
EMAIL_PASSWORD = "your_password"        # App password ONLY
EMAIL_TO = "nandaprasadmp@gmail.com"

def send_email_alert(subject, image_path=None):
    """
    Send alert email with optional image attachment.
    """
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg["Subject"] = subject

        msg.set_content("Alert Triggered: " + subject)

        # Attach image if provided
        if image_path:
            with open(image_path, "rb") as f:
                img_data = f.read()
            msg.add_attachment(
                img_data,
                maintype="image",
                subtype="jpeg",
                filename=Path(image_path).name
            )

        # Send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)

        print("📧 Email sent successfully!")

    except Exception as e:
        print("❌ Email error:", e)
