import smtplib
from email.message import EmailMessage

from app.config.settings import (
    MAIL_EMAIL,
    MAIL_APP_PASSWORD,
    FRONTEND_URL,
)


def send_reset_email(to_email: str, token: str):
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    msg = EmailMessage()

    msg["Subject"] = "AI MISINFO - Password Reset Request"
    msg["From"] = MAIL_EMAIL
    msg["To"] = to_email

    msg.set_content(
        f"""
Hello,

We received a request to reset the password for your AI MISINFO account.

To create a new password, click the secure link below:

{reset_link}

Important:
• This link is valid for only 15 minutes.
• If you did not request a password reset, you can safely ignore this email.
• Your password will remain unchanged unless you complete the reset process.

Thank you,

AI MISINFO Team
"""
    )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(MAIL_EMAIL, MAIL_APP_PASSWORD)
            smtp.send_message(msg)

        print(f"✅ Password reset email sent to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise