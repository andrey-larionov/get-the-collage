# Enable development environment
DEBUG = True

# Define app directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database connection
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'migrations')
DATABASE_CONNECT_OPTIONS = {}

# Upload image directory
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# Instagram client ID
INSTAGRAM_CLIENT_ID = "CLIENT_ID"
INSTAGRAM_SECRET = "SECRET"
INSTAGRAM_REDIRECT_URI = "http://localhost:5000/oauth"

CSRF_ENABLED = True

# App secret key
SECRET_KEY = 'agd17t7sdvjaf61t36'