import os

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "postgresql://user:password@postgres:5432/postgres")
SECRET_KEY = os.environ.get("SECRET_KEY", "aZ1x9vqfK2w+G+dwiXm16BnyhsJXgsmwuIiLNqKDRI/8x7axAscKc7Dg")
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
frame_options_allow_from = os.environ.get("FRAME_OPTIONS_ALLOW_FROM", "http://localhost:3000")
TALISMAN_CONFIG = {
    "frame_options_allow_from": [frame_options_allow_from]
}

cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'origins': cors_origins,
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
}
