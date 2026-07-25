from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def main():
    # Create SQLAlchemy engine using the same connection string
    engine = create_engine('')
    
    # Method 1: Using engine.connect() (similar to your psycopg2 approach)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT VERSION()'))
        version = result.fetchone()[0]
        print("Using engine.connect():", version)
    
    # Method 2: Using sessionmaker (ORM approach)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        result = session.execute(text('SELECT VERSION()'))
        version = result.fetchone()[0]
        print("Using session:", version)
    finally:
        session.close()
    
    # Method 3: Using session context manager (recommended)
    with Session() as session:
        result = session.execute(text('SELECT VERSION()'))
        version = result.fetchone()[0]
        print("Using session context manager:", version)

if __name__ == "__main__":
    main()