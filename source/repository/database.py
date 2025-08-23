from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from source.config.config import database_config

class Database:
    def __init__(self):
        self.engine = create_engine(database_config.SQLALCHEMY_DATABASE_URI)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    def get_db(self):
        """Get a database session"""
        try:
            session = self.SessionLocal()
            print(f"DEBUG: Database session created: {session}")
            return session
        except Exception as e:
            print(f"DEBUG: Error creating database session: {e}")
            raise

    def get_base(self):
        return self.Base

db = Database()
engine = db.engine 
Base = db.get_base()
get_db = db.get_db
