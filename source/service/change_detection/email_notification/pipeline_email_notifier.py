from source.service.change_detection.email_notification.email_utils import EmailSender
from source.repository.user.repository import UserRepository
from source.repository.user_pipeline_access.repository import UserPipelineAccessRepository


class PipelineEmailNotifier:
    def __init__(self, pipeline_id, email_sender: EmailSender, pipeline_name=None, human_readable_message=None, technical_details=None):
        self.pipeline_id = pipeline_id
        self.email_sender = email_sender
        self.user_repo = UserRepository()
        self.access_repo = UserPipelineAccessRepository()
        self.pipeline_name = pipeline_name or "N/A"
        self.human_readable_message = human_readable_message or ""
        self.technical_details = technical_details or ""

    def get_recipients(self):
        all_users = self.user_repo.get_all_active_user()
        admins = [user for user in all_users if getattr(user, 'role', None) == 'admin']
        admin_emails = [user.email for user in admins]
        users = self.access_repo.get_users_for_pipeline(self.pipeline_id)
        user_emails = [user.email for user in users]
        all_emails = set(admin_emails + user_emails)
        return list(all_emails)

    def send_schema_change_notification(self):
        subject = f"Schema Change Detected for Pipeline {self.pipeline_id}"
        message = (
            f"A schema change was detected for pipeline '{self.pipeline_name}' (ID: {self.pipeline_id}).\n\n"
            f"--- What Happened ---\n"
            f"{self.human_readable_message}\n\n"
            f"--- Breaking Change: YES ---\n"
            f"⚠️  WARNING: This is a breaking change that will affect your data pipeline!"
        )
        recipients = self.get_recipients()
        for email in recipients:
            self.email_sender.send_email(email, subject, message)