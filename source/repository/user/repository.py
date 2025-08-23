import logging
from typing import Optional, Dict, Any, List
from source.models.user.models import User
from source.repository.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self):
        pass
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username (including deleted users)
        
        Args:
            username: User's username
            
        Returns:
            User object or None if not found
        """
        if not username:
            logger.warning("Attempted to get user with empty username")
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user:
                logger.debug(f"Found user by username: {username}")
            else:
                logger.debug(f"No user found with username: {username}")
            return user
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {str(e)}")
            raise
        finally:
            db.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get active user by email
        
        Args:
            email: User's email
            
        Returns:
            User object or None if not found
        """
        if not email:
            logger.warning("Attempted to get user with empty email")
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
            if user:
                logger.debug(f"Found active user by email: {email}")
            else:
                logger.debug(f"No active user found with email: {email}")
            return user
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            raise
        finally:
            db.close()

    def get_user_by_email_and_username(self, email: str, username: str) -> Optional[User]:
        """
        Get user by email or username (including deleted users)
        
        Args:
            email: User's email
            username: User's username
            
        Returns:
            User object or None if not found
        """
        if not email and not username:
            logger.warning("Attempted to get user with empty email and username")
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
                logger.debug(f"Found user by email/username: {email}/{username}")
            else:
                logger.debug(f"No user found with email/username: {email}/{username}")
            return user
        except Exception as e:
            logger.error(f"Error getting user by email/username {email}/{username}: {str(e)}")
            raise
        finally:
            db.close()

    def get_active_user_by_username(self, username: str) -> Optional[User]:
        """
        Get active user by username
        
        Args:
            username: User's username
            
        Returns:
            User object or None if not found
        """
        if not username:
            logger.warning("Attempted to get active user with empty username")
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.username.ilike(username), User.is_deleted == False).first()
            if user:
                logger.debug(f"Found active user by username: {username}")
            else:
                logger.debug(f"No active user found with username: {username}")
            return user
        except Exception as e:
            logger.error(f"Error getting active user by username {username}: {str(e)}")
            raise
        finally:
            db.close()

    def get_all_active_user(self) -> List[User]:
        """
        Get all active users
        
        Returns:
            List of active users
        """
        db = get_db()
        try:
            users = db.query(User).filter(User.is_deleted == False).all()
            logger.debug(f"Retrieved {len(users)} active users")
            return users
        except Exception as e:
            logger.error(f"Error getting all active users: {str(e)}")
            raise
        finally:
            db.close()
    
    def get_all_users_filtered(self, search: str = None, role: str = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get all users with filtering and pagination
        
        Args:
            search: Search term for username, email, first_name, or last_name
            role: Filter by user role
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            Dict containing users, total count, and pagination info
        """
        # Validate pagination parameters
        if limit <= 0 or limit > 1000:
            limit = 100
            logger.warning(f"Invalid limit {limit}, using default value 100")
        if offset < 0:
            offset = 0
            logger.warning(f"Invalid offset {offset}, using default value 0")
            
        db = get_db()
        try:
            query = db.query(User).filter(User.is_deleted == False)
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (User.username.ilike(search_filter)) |
                    (User.email.ilike(search_filter)) |
                    (User.first_name.ilike(search_filter)) |
                    (User.last_name.ilike(search_filter))
                )
                logger.debug(f"Applied search filter: {search}")
            
            if role and role != 'all':
                query = query.filter(User.role == role)
                logger.debug(f"Applied role filter: {role}")
            
            total_count = query.count()
            users = query.offset(offset).limit(limit).all()
            
            logger.debug(f"Retrieved {len(users)} users out of {total_count} total (limit: {limit}, offset: {offset})")
            
            return {
                "users": users,
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            }
        except Exception as e:
            logger.error(f"Error getting filtered users: {str(e)}")
            raise
        finally:
            db.close()

    def get_active_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get active user by ID
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User object or None if not found
        """
        if not user_id:
            logger.warning("Attempted to get active user with empty user ID")
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()
            if user:
                logger.debug(f"Found active user by ID: {user_id}")
            else:
                logger.debug(f"No active user found with ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error getting active user by ID {user_id}: {str(e)}")
            raise
        finally:
            db.close()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID (including deleted users)
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User object or None if not found
        """
        if not user_id:
            logger.warning("Attempted to get user with empty user ID")
            return None
            
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                logger.debug(f"Found user by ID: {user_id}")
            else:
                logger.debug(f"No user found with ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise
        finally:
            db.close()

    def create_user(self, user: User) -> User:
        """
        Create a new user
        
        Args:
            user: User object to create
            
        Returns:
            Created user object
            
        Raises:
            Exception: If user creation fails
        """
        if not user or not user.user_id or not user.username or not user.email:
            logger.error("Invalid user data provided for creation")
            raise ValueError("Invalid user data: user_id, username, and email are required")
            
        db = get_db()
        try:
            logger.info(f"Creating user: {user.username} ({user.user_id})")
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User {user.username} created successfully")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user {user.username}: {str(e)}")
            raise
        finally:
            db.close()

    def mark_deleted(self, user: User) -> None:
        """
        Mark a user as deleted (soft delete)
        
        Args:
            user: User object to mark as deleted
            
        Raises:
            Exception: If marking as deleted fails
        """
        if not user:
            logger.error("Cannot mark deleted: user object is None")
            raise ValueError("User object cannot be None")
            
        db = get_db()
        try:
            logger.info(f"Marking user {user.username} ({user.user_id}) as deleted")
            user.is_deleted = True
            db.commit()
            logger.info(f"User {user.username} marked as deleted successfully")
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking user {user.username} as deleted: {str(e)}")
            raise
        finally:
            db.close()

    def commit(self) -> None:
        """
        Commit pending database changes
        
        Raises:
            Exception: If commit fails
        """
        db = get_db()
        try:
            db.commit()
            logger.debug("Database changes committed successfully")
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing database changes: {str(e)}")
            raise
        finally:
            db.close()
