# User Service

This module manages user accounts, authentication, and integration with Superset, supporting user creation, login, updates, and deletion.

---

## Main Class

### UserService
Handles all business logic related to user management, authentication, and Superset account integration.

**Key Methods:**
- `__init__(self)`: Initializes the user repository, authentication service, and Superset integration.
- `signup(self, user_data)`: Registers a new user, hashes their password, and creates a Superset account.
- `get_all_users(self)`: Returns all active users.
- `get_user_by_id(self, user_id)`: Retrieves a user by their ID.
- `get_user_by_username(self, username)`: Retrieves a user by their username.
- `delete_user(self, user_id)`: Soft-deletes a user by ID.
- `update_password(self, password_data)`: Updates a user's password after verifying the old password.
- `update_user(self, user_data)`: Updates user information (email, username, first/last name).
- `login(self, login_data)`: Authenticates a user and returns a JWT access token.

---

Use this module to:
- Manage user accounts and authentication.
- Integrate user management with Superset for analytics access.
- Support secure login, registration, and user profile updates. 