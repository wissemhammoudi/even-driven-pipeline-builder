# User Superset Account Association Service

This module manages the association between application users and their corresponding Superset accounts, enabling integration and permission mapping for analytics access.

---

## Main Class

### UserSupersetAccountAssociationService
Handles creation and retrieval of associations between users and Superset accounts.

**Key Methods:**
- `__init__(self)`: Initializes the association repository.
- `add_association(self, user_id, superset_user_id)`: Creates an association between an app user and a Superset user.
- `get_by_user_id(self, user_id)`: Retrieves all Superset associations for a given user.

---

Use this module to:
- Link application users to their Superset accounts for analytics and dashboard access.
- Retrieve Superset associations for permission management and integration. 