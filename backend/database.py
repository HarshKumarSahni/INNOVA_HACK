import os
from dotenv import load_dotenv

# Load .env from current directory or backend/.env
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Option 1: Use environment variable (recommended for production)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Fix postgres:// legacy schema from Aiven/Heroku/Render for SQLAlchemy 1.4+
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


engine = create_engine(
    DATABASE_URL,
    # Optional: Add connection pool settings for better performance
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Validates connections before use
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Helper function to get database sessions
def get_db():
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test the connection
def test_connection():
    """Test if database connection works"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()