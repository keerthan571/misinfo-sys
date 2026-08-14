import resend

from app.config.settings import (
    RESEND_API_KEY,
    FRONTEND_URL,
)


def send_reset_email(to_email: str, token: str):

    reset_link = (
        f"{FRONTEND_URL}/reset-password?token={token}"
    )

    resend.api_key = RESEND_API_KEY

    params = {
        "from": "AI MISINFO <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "AI MISINFO - Password Reset Request",
        "html": f"""
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: auto;
            padding: 30px;
            color: #1e293b;
        ">

            <h2 style="color: #2563eb;">
                AI MISINFO
            </h2>

            <h3>
                Password Reset Request
            </h3>

            <p>
                Hello,
            </p>

            <p>
                We received a request to reset the password
                for your AI MISINFO account.
            </p>

            <p>
                Click the button below to create a new password:
            </p>

            <p style="margin: 30px 0;">
                <a
                    href="{reset_link}"
                    style="
                        background: #2563eb;
                        color: white;
                        padding: 12px 22px;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                    "
                >
                    Reset Password
                </a>
            </p>

            <p>
                This link is valid for only
                <strong>15 minutes</strong>.
            </p>

            <p>
                If you did not request a password reset,
                you can safely ignore this email.
            </p>

            <hr style="
                border: none;
                border-top: 1px solid #e2e8f0;
                margin: 30px 0;
            ">

            <p style="
                color: #64748b;
                font-size: 13px;
            ">
                AI MISINFO Team
            </p>

        </div>
        """,
    }

    try:

        email = resend.Emails.send(params)

        print(
            f"Password reset email sent to {to_email}"
        )

        print(
            f"Resend response: {email}"
        )

        return email

    except Exception as e:

        print(
            f"Failed to send password reset email: {e}"
        )

        raise