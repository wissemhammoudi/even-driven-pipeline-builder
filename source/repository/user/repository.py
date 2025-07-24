from source.models.user.models import User
from source.repository.database import get_db
database= get_db()

class UserRepository:
    def __init__(self):
        self.db = database
    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email,User.is_deleted == False).first()

    def get_user_by_email_and_username(self, email: str, username:str):
        return self.db.query(User).filter((User.email == email) | (User.username == username), User.is_deleted == False).first()

    def get_active_user_by_username(self, username: str)->User:
        return self.db.query(User).filter(User.username.ilike(username), User.is_deleted == False).first()

    def get_all_active_user(self):
        return self.db.query(User).filter(User.is_deleted == False).all()

    def get_active_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.user_id == user_id).first()

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def mark_deleted(self, user:User):
        user.is_deleted = True
        self.db.commit()

    def commit(self):
        self.db.commit()
