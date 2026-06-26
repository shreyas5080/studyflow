import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")


def send_otp_email(to_email: str, otp: str):
    if not BREVO_API_KEY:
        raise HTTPException(status_code=500, detail="BREVO_API_KEY missing")

    payload = {
        "sender": {"name": "StudyFlow", "email": "shreyaspojari567@gmail.com"},
        "to": [{"email": to_email}],
        "subject": "Your StudyFlow verification code",
        "htmlContent": f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.5;">
            <h2>Your StudyFlow verification code</h2>
            <p>Hello,</p>
            <p>Use this code to verify your email address:</p>
            <p style="font-size: 24px; font-weight: bold; letter-spacing: 4px;">
                {otp}
            </p>
            <p>This code will expire soon. If you didn’t request this, you can ignore this email.</p>
            <p>Thanks,<br>StudyFlow Team</p>
        </div>
        """,
        "textContent": f"""
Your StudyFlow verification code is: {otp}

Use this code to verify your email address.

If you didn’t request this, you can ignore this email.

Thanks,
StudyFlow Team
""",
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=15,
        )

        if response.status_code >= 400:
            print("BREVO ERROR:", response.status_code, response.text)
            raise HTTPException(
                status_code=500, detail=f"Email failed: {response.text}"
            )

    except requests.RequestException as e:
        print("BREVO REQUEST ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"Email failed: {str(e)}")
