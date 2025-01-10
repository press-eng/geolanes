from email.message import EmailMessage

import aiosmtplib

from lib import config


async def send_otp_email(otp: str, email: str):
    message = EmailMessage()
    message["From"] = config.SMTP_SENDER_EMAIL
    message["To"] = email
    message["Subject"] = "OTP | Geolanes"
    message.set_content(otp)

    await aiosmtplib.send(
        message,
        hostname=config.SMTP_SERVER,
        port=config.SMTP_PORT,
        validate_certs=False,
    )
