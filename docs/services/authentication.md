# Authentication Service

This module provides authentication and authorization logic, including password hashing, user verification, and JWT token management for secure API access.

---

## Main Class

### AuthService
Handles user authentication, password management, and JWT-based access token creation and validation.

**Key Methods:**
- `__init__(self, user_repo, secret_key, algorithm, token_expiry_minutes)`: Initializes the service with user repository and JWT settings.
- `hash_password(self, password)`: Hashes a plain password using bcrypt.
- `verify_password(self, plain_password, hashed_password)`: Verifies a plain password against a hash.
- `authenticate_user(self, email, password)`: Authenticates a user by email and password, returns the user if valid.
- `create_access_token(self, user)`: Creates a JWT access token for the given user.
- `get_current_user(self, token)`: Decodes a JWT token and returns the corresponding user, or raises an error if invalid.

---

Use this module to:
- Secure your API endpoints with JWT authentication.
- Manage user login, password hashing, and token validation.
- Integrate with FastAPI dependency injection for protected routes. 