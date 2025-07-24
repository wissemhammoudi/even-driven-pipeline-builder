from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from source.config.config import DatabaseConfig
class Database:
    def __init__(self):
        self.engine = create_engine(DatabaseConfig.SQLALCHEMY_DATABASE_URI)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    def get_db(self):
        db = self.SessionLocal()
        try:
            return db
        finally:
            db.close()

    def get_base(self):
        return self.Base

db = Database()
engine = db.engine 
Base = db.get_base()
get_db = db.get_db
