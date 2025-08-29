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
            logger.warning("Attempted to get active user with empty email")
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
            logger.error(f"Error getting active user by email {email}: {str(e)}")
            raise
        finally:
            db.close()

    def get_user_by_email_and_username(self, email: str = None, username: str = None) -> Optional[User]:
        """
        Get user by email and/or username (active users only)
        
        Args:
            email: User's email address
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
            logger.info("Retrieving all active users from database...")
            
            # Query for active users
            query = db.query(User).filter(User.is_deleted == False)
            logger.debug(f"Executing query: {query}")
            
            users = query.all()
            logger.info(f"✅ Retrieved {len(users)} active users from database")
            
            # Log user details for debugging
            for user in users:
                logger.debug(f"  - {user.username} (ID: {user.user_id}, role: {user.role.value})")
            
            return users
        except Exception as e:
            logger.error(f"Error getting all active users: {str(e)}")
            raise
        finally:
            db.close()
            logger.debug("Database session closed")
    
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
        if offset < 0:
            offset = 0
            
        db = get_db()
        try:
            logger.info(f"Retrieving filtered users with search='{search}', role='{role}', limit={limit}, offset={offset}")
            
            # Build base query
            query = db.query(User).filter(User.is_deleted == False)
            
            # Apply search filter if provided
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    (User.username.ilike(search_term)) |
                    (User.email.ilike(search_term)) |
                    (User.first_name.ilike(search_term)) |
                    (User.last_name.ilike(search_term))
                )
                logger.debug(f"Applied search filter: {search_term}")
            
            # Apply role filter if provided
            if role:
                query = query.filter(User.role == role)
                logger.debug(f"Applied role filter: {role}")
            
            # Get total count before pagination
            total_count = query.count()
            logger.debug(f"Total users matching filters: {total_count}")
            
            # Apply pagination
            users = query.offset(offset).limit(limit).all()
            logger.info(f"✅ Retrieved {len(users)} users (page {offset//limit + 1})")
            
            # Log user details for debugging
            for user in users:
                logger.debug(f"  - {user.username} (ID: {user.user_id}, role: {user.role.value})")
            
            return {
                "users": users,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "page": (offset // limit) + 1,
                "total_pages": (total_count + limit - 1) // limit
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
            logger.info(f"Creating user in database: {user.username} ({user.user_id})")
            
            # Add user to session
            db.add(user)
            logger.debug("User added to session")
            
            # Commit the transaction
            db.commit()
            logger.debug("Transaction committed")
            
            # Refresh the user object to get any auto-generated values
            db.refresh(user)
            logger.debug("User object refreshed")
            
            logger.info(f"✅ User {user.username} created successfully in database")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user {user.username}: {str(e)}")
            db.rollback()
            logger.debug("Transaction rolled back")
            raise
        finally:
            db.close()
            logger.debug("Database session closed")

    def mark_deleted(self, user_id: str) -> None:
        """
        Mark a user as deleted (soft delete)
        
        Args:
            user_id: User ID to mark as deleted
            
        Raises:
            Exception: If marking as deleted fails
        """
        if not user_id:
            logger.error("❌ Cannot mark deleted: user_id is None")
            raise ValueError("User ID cannot be None")
            
        db = get_db()
        try:
            logger.info(f"💾 Starting to mark user {user_id} as deleted")
            
            # Get the user in the current session
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                logger.error(f"❌ User {user_id} not found")
                raise ValueError(f"User {user_id} not found")
            
            logger.info(f"🔍 Current user state - is_deleted: {user.is_deleted}")
            
            user.is_deleted = True
            logger.info(f"✅ User {user.username} marked as deleted in memory")
            
            db.commit()
            logger.info(f"💾 Database transaction committed for user {user.username}")
            
            logger.info(f"🎉 User {user.username} marked as deleted successfully")
        except Exception as e:
            logger.error(f"❌ Error marking user {user_id} as deleted: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            db.rollback()
            logger.info(f"🔄 Database transaction rolled back")
            raise
        finally:
            db.close()

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Update user fields
        
        Args:
            user_id: User ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated user object or None if not found
            
        Raises:
            Exception: If update fails
        """
        if not user_id:
            logger.error("❌ Cannot update: user_id is None")
            raise ValueError("User ID cannot be None")
            
        db = get_db()
        try:
            logger.info(f"💾 Starting to update user {user_id}")
            
            # Get the user in the current session
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                logger.error(f"❌ User {user_id} not found")
                return None
            
            logger.info(f"🔍 Current user state: {user.username}")
            
            # Update fields
            for field, value in kwargs.items():
                if hasattr(user, field) and value is not None:
                    # Special handling for role field
                    if field == 'role' and isinstance(value, str):
                        # Validate role value
                        if value.lower() not in ['user', 'admin']:
                            raise ValueError(f"Invalid role: {value}. Must be 'user' or 'admin'")
                        # Convert to proper enum value
                        from source.schema.user.schemas import UserRole
                        if value.lower() == 'admin':
                            value = UserRole.admin
                        else:
                            value = UserRole.user
                    
                    setattr(user, field, value)
                    logger.info(f"✅ Updated {field} to {value}")
            
            db.commit()
            logger.info(f"💾 Database transaction committed for user {user.username}")
            
            # Refresh to get updated values
            db.refresh(user)
            logger.info(f"🎉 User {user.username} updated successfully")
            
            return user
        except Exception as e:
            logger.error(f"❌ Error updating user {user_id}: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            db.rollback()
            logger.info(f"🔄 Database transaction rolled back")
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

    def rollback(self) -> None:
        """
        Rollback pending database changes
        """
        db = get_db()
        try:
            db.rollback()
            logger.debug("Database changes rolled back successfully")
        except Exception as e:
            logger.error(f"Error rolling back database changes: {str(e)}")
            raise
        finally:
            db.close()
