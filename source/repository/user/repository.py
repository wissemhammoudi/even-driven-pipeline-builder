from typing import Optional, Dict, Any, List
from source.models.user.models import User
from source.repository.database import get_db

class UserRepository:
    def __init__(self):
        pass

    def get_user_by_username(self, username: str) -> Optional[User]:
        
        if not username:
            return None            
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user:
                return user
        except Exception as e:
            raise Exception(f"Failed to get user by username: {str(e)}")
        finally:
            db.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        
        if not email:
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
            if user:
                return user
        except Exception as e:
            raise Exception(f"Failed to get user by email: {str(e)}")
        finally:
            db.close()

    def get_user_by_email_and_username(self, email: str = None, username: str = None) -> Optional[User]:

        if not email and not username:
            return None
            
        db = get_db()
        try:
            query = db.query(User).filter(User.is_deleted == False)
            
            if email and username:
                query = query.filter((User.email == email) | (User.username == username))
            elif email:
                query = query.filter(User.email == email)
            elif username:
                query = query.filter(User.username == username)
            
            user = query.first()
            if user:
                return user
        except Exception as e:
            raise Exception(f"Failed to get user by email and username: {str(e)}")
        finally:
            db.close()

    def get_active_user_by_username(self, username: str) -> Optional[User]:

        if not username:
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.username.ilike(username), User.is_deleted == False).first()
            if user:
                return user
        except Exception as e:
            raise Exception(f"Failed to get active user by username: {str(e)}")
        finally:
            db.close()

    def get_all_active_user(self) -> List[User]:
        
        db = get_db()
        try:
            query = db.query(User).filter(User.is_deleted == False)
            users = query.all()
            return users
        except Exception as e:
            raise Exception(f"Failed to get active users: {str(e)}")
        finally:
            db.close()
    
    def get_all_users_filtered(self, search: str = None, role: str = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        
        if limit <= 0 or limit > 1000:
            limit = 100
        if offset < 0:
            offset = 0
            
        db = get_db()
        try:
            query = db.query(User).filter(User.is_deleted == False)
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    (User.username.ilike(search_term)) |
                    (User.email.ilike(search_term)) |
                    (User.first_name.ilike(search_term)) |
                    (User.last_name.ilike(search_term))
                )
            
            if role:
                query = query.filter(User.role == role)
            
            total_count = query.count()
            users = query.offset(offset).limit(limit).all()            
            return {
                "users": users,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "page": (offset // limit) + 1,
                "total_pages": (total_count + limit - 1) // limit
            }
            
        except Exception as e:
            raise KeyError(f"Error getting filtered users: {str(e)}")
        finally:
            db.close()

    def get_active_user_by_id(self, user_id: str) -> Optional[User]:
        
        if not user_id:
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()
            if user:
                return user
        except Exception as e:
            raise Exception(f"Failed to get active user by ID: {str(e)}")
        finally:
            db.close()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        
        if not user_id:
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                return user
        except Exception as e:
            raise Exception(f"Failed to get user by ID: {str(e)}")
        finally:
            db.close()

    def create_user(self, user: User) -> Optional[User]:
        
        if not user or not user.user_id or not user.username or not user.email:
            raise ValueError("Invalid user data: user_id, username, and email are required")
            
        db = get_db()
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create user: {str(e)}")
        finally:
            db.close()

    def mark_deleted(self, user_id: str) -> None:
        
        if not user_id:
            raise ValueError("User ID cannot be None")
            
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            user.is_deleted = True
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to mark user as deleted: {str(e)}")
        finally:
            db.close()

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        
        if not user_id:
            raise ValueError("User ID cannot be None")
            
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None
            
            for field, value in kwargs.items():
                if hasattr(user, field) and value is not None:
                    if field == 'role' and isinstance(value, str):
                        if value.lower() not in ['user', 'admin']:
                            raise ValueError(f"Invalid role: {value}. Must be 'user' or 'admin'")
                        from source.schema.user.schemas import UserRole
                        if value.lower() == 'admin':
                            value = UserRole.admin
                        else:
                            value = UserRole.user
                    
                    setattr(user, field, value)  
            db.commit() 
            db.refresh(user)
            
            return user
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to update user: {str(e)}")
        finally:
            db.close()

    def commit(self) -> None:
        
        db = get_db()
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to commit transaction: {str(e)}")
        finally:
            db.close()

    def rollback(self) -> None:
        
        db = get_db()
        try:
            db.rollback()
        except Exception as e:
            raise Exception(f"Failed to rollback transaction: {str(e)}")
        finally:
            db.close()
