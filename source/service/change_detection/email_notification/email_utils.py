import smtplib
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self, smtp_server, port, username, password, use_tls=True):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send_email(self, to_email, subject, message, from_email=None):
        from_email = from_email or self.username
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        with smtplib.SMTP(self.smtp_server, self.port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.sendmail(from_email, [to_email], msg.as_string())