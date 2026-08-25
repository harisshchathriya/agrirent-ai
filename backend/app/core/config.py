from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "")
SECRET_KEY: str = os.getenv("SECRET_KEY", "")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")
