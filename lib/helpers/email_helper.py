import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from lib import config

smtp_server = config.SMTP_SERVER
smtp_port = config.SMTP_PORT
smtp_sender = config.SMTP_SENDER_EMAIL


def send_smtp_email(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    recipient_email: str,
    subject: str,
    message: str,
):
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Attach the message body
        msg.attach(MIMEText(message, "plain"))

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection

            # Send the email
            server.sendmail(sender_email, recipient_email, msg.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")


def send_email_with_template(
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    recipient_email: str,
    reset_link: str,
):
    try:
        # Email subject and message content
        subject = "Set Your New Password"
        html_content = f"""
        <html>
        <body>
            <h2 style="color: #333;">Set Your New Password</h2>
            <p>Hi,</p>
            <p>Welcome to Enterprise portal! You can set a new password by clicking the link below:</p>
            <a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Set New Password
            </a>
            <p>If you did not request this, please ignore this email.</p>
            <p>Thanks, <br>GeoLanes</p>
        </body>
        </html>
        """

        # Create email message container
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Attach the HTML content to the email
        msg.attach(MIMEText(html_content, "html"))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.sendmail(sender_email, recipient_email, msg.as_string())

        print("Password reset email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")
