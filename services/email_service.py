import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO


class EmailService:
    def __init__(
        self, smtp_server: str, smtp_port: int, smtp_username: str, smtp_password: str
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: list[tuple[str, BytesIO]] | None = None,
    ):
        msg = MIMEMultipart()
        msg["From"] = self.smtp_username
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        if attachments:
            for filename, file_buffer in attachments:
                file_buffer.seek(0)
                part = MIMEApplication(file_buffer.read(), Name=filename)
                part["Content-Disposition"] = f'attachment; filename="{filename}"'
                msg.attach(part)

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
