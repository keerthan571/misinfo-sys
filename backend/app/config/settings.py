from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
)

MAIL_EMAIL = os.getenv("MAIL_EMAIL")
MAIL_APP_PASSWORD = os.getenv("MAIL_APP_PASSWORD")

FRONTEND_URL = os.getenv("FRONTEND_URL")