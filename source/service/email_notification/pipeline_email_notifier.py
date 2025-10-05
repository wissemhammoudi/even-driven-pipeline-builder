import os
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional


class PipelineEmailNotifier:
    """
    A class for sending email notifications about pipeline schema changes.
    """
    
    def __init__(self, pipeline_id: int, pipeline_name: str, 
                 human_readable_message: str, technical_details: str, 
                 is_breaking: bool):
        """
        Initialize the email notifier with schema change details.
        """
        self.pipeline_id = pipeline_id
        self.pipeline_name = pipeline_name
        self.human_readable_message = human_readable_message
        self.technical_details = technical_details
        self.is_breaking = is_breaking
        
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "pipeline-alerts@example.com")
        
        self.default_recipients = ["admin@example.com"]
        if os.getenv("ALERT_RECIPIENTS"):
            try:
                self.default_recipients = os.getenv("ALERT_RECIPIENTS").split(",")
            except Exception as e:
                pass
    
    def send_schema_change_notification(self, recipients: Optional[List[str]] = None) -> bool:
        """
        Send an email notification about the schema change.

        """
        try:
            to_emails = recipients if recipients else self.default_recipients
            
            severity = "🚨 BREAKING" if self.is_breaking else "ℹ️ Non-breaking"
            subject = f"{severity} Schema Change Alert - Pipeline: {self.pipeline_name} (ID: {self.pipeline_id})"
            
            body = self._create_email_body()
            
            asyncio.create_task(self._send_email_async(to_emails, subject, body))
            
            return True
        except Exception as e:
            return False
    
    def _create_email_body(self) -> str:
        """
        Create the HTML body for the schema change notification email.

        """
        status_color = "#FF0000" if self.is_breaking else "#FFA500"
        status_text = "BREAKING CHANGE - Pipeline Marked as BROKEN" if self.is_breaking else "Non-breaking Change"
        
        return f"""
        <html>
        <body>
            <h2>Schema Change Notification</h2>
            <p>A schema change has been detected in your data pipeline.</p>
            
            <h3>Pipeline Information</h3>
            <ul>
                <li><strong>Pipeline ID:</strong> {self.pipeline_id}</li>
                <li><strong>Pipeline Name:</strong> {self.pipeline_name}</li>
                <li><strong>Status:</strong> <span style="color: {status_color};">{status_text}</span></li>
            </ul>
            
            <h3>Change Description</h3>
            <p>{self.human_readable_message}</p>
            
            <h3>Technical Details</h3>
            <pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">
{self.technical_details}
            </pre>
            
            <p>Please review the schema change and update your pipeline configuration if necessary.</p>
            
            <hr>
            <p><small>This is an automated notification from the Event-Driven Pipeline Builder.</small></p>
        </body>
        </html>
        """
    
    async def _send_email_async(self, to_emails: List[str], subject: str, body: str) -> bool:
        """
        Asynchronously send an email.
        """
        try:
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = ", ".join(to_emails)
            message["Subject"] = subject
            
            message.attach(MIMEText(body, "html"))
            
            if not self.smtp_username or not self.smtp_password:
                return False
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            return False