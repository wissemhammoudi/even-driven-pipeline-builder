import os

SQLALCHEMY_DATABASE_URI = "postgresql://user:password@postgres:5432/postgres"
SECRET_KEY ="aZ1x9vqfK2w+G+dwiXm16BnyhsJXgsmwuIiLNqKDRI/8x7axAscKc7Dg"
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
ENABLE_PROXY_FIX = True

FAB_ADD_SECURITY_API = True
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
        "ENABLE_API": True,
    "ENABLE_REACT_CRUD_VIEWS": True,
}


TALISMAN_ENABLED = False
# or configure Talisman properly:
TALISMAN_CONFIG = {
    "frame_options": "SAMEORIGIN",  # or "ALLOWALL" for any domain
    "frame_options_allow_from": ["http://localhost:3000"]  # your frontend URL
}

# Configure CORS
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'origins': ['http://localhost:3000'],  # your frontend URL
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
}
