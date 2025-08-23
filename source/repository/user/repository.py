from source.models.user.models import User
from source.repository.database import get_db

class UserRepository:
    def __init__(self):
        pass
    
    def get_user_by_username(self, username: str):
        db = get_db()
        try:
            return db.query(User).filter(User.username == username).first()
        finally:
            db.close()

    def get_user_by_email(self, email: str):
        db = get_db()
        try:
            return db.query(User).filter(User.email == email, User.is_deleted == False).first()
        finally:
            db.close()

    def get_user_by_email_and_username(self, email: str, username:str):
        db = get_db()
        try:
            return db.query(User).filter((User.email == email) | (User.username == username), User.is_deleted == False).first()
        finally:
            db.close()

    def get_active_user_by_username(self, username: str)->User:
        db = get_db()
        try:
            return db.query(User).filter(User.username.ilike(username), User.is_deleted == False).first()
        finally:
            db.close()

    def get_all_active_user(self):
        db = get_db()
        try:
            print(f"DEBUG: Querying all active users...")
            users = db.query(User).filter(User.is_deleted == False).all()
            print(f"DEBUG: Found {len(users)} active users")
            for user in users:
                print(f"DEBUG: User: {user.username} (ID: {user.user_id})")
            return users
        except Exception as e:
            print(f"DEBUG: Error querying users: {e}")
            raise
        finally:
            db.close()
    
    def get_all_users_filtered(self, search: str = None, role: str = None, limit: int = 100, offset: int = 0):
        """Get all users with filtering and pagination"""
        db = get_db()
        try:
            print(f"DEBUG: Getting filtered users - search: {search}, role: {role}, limit: {limit}, offset: {offset}")
            query = db.query(User).filter(User.is_deleted == False)
            
            # Apply search filter
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (User.username.ilike(search_filter)) |
                    (User.email.ilike(search_filter)) |
                    (User.first_name.ilike(search_filter)) |
                    (User.last_name.ilike(search_filter))
                )
            
            # Apply role filter
            if role and role != 'all':
                query = query.filter(User.role == role)
            
            # Apply pagination
            total_count = query.count()
            users = query.offset(offset).limit(limit).all()
            
            print(f"DEBUG: Found {total_count} total users, returning {len(users)} users")
            
            return {
                "users": users,
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            }
        except Exception as e:
            print(f"DEBUG: Error getting filtered users: {e}")
            raise
        finally:
            db.close()

    def get_active_user_by_id(self, user_id: str):
        db = get_db()
        try:
            return db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()
        finally:
            db.close()

    def get_user_by_id(self, user_id: str):
        db = get_db()
        try:
            return db.query(User).filter(User.user_id == user_id).first()
        finally:
            db.close()

    def create_user(self, user: User):
        db = get_db()
        try:
            print(f"DEBUG: Adding user to database: {user.username}")
            db.add(user)
            print(f"DEBUG: Committing user to database...")
            db.commit()
            print(f"DEBUG: Refreshing user object...")
            db.refresh(user)
            print(f"DEBUG: User successfully created: {user.user_id}")
            return user
        except Exception as e:
            print(f"DEBUG: Error creating user: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def mark_deleted(self, user:User):
        db = get_db()
        try:
            user.is_deleted = True
            db.commit()
        finally:
            db.close()

    def commit(self):
        db = get_db()
        try:
            db.commit()
        finally:
            db.close()
