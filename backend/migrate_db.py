# backend/migrate_db.py
from database import engine
from sqlalchemy import text

def run_migration():
    print("🚀 Starting database migration...")
    try:
        with engine.connect() as connection:
            # Add the missing column
            print("--- Adding is_authorized column to users table ---")
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_authorized BOOLEAN DEFAULT FALSE;"))
            
            # Manually authorize your account (replace with your email)
            print("--- Authorizing admin user ---")
            # EDIT THIS LINE: Change 'vanneet@gmail.com' to your actual email
            email_to_authorize = 'rad@gmail.com' 
            connection.execute(text(f"UPDATE users SET is_authorized = TRUE WHERE email = '{email_to_authorize}';"))
            
            connection.commit()
            print("✅ Migration successful! The column is added and your user is authorized.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()