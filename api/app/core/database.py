from sqlalchemy import create_engine
# from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import SETTINGS


# Construct the SQLAlchemy connection string
DATABASE_URL = SETTINGS.DATABASE_URL
print(DATABASE_URL, 'databaseurl')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Test the connection
def get_db():
    try:
        with engine.connect() as connection:
            print("Connection successful!")
            yield SessionLocal()
    except Exception as e:
        print(f"Failed to connect: {e}")