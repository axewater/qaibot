# bot/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # Import the Base from models.py
from .config import SQLALCHEMY_DATABASE_URI
import logging
from urllib.parse import urlparse

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)  # Set echo to False in production
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    """Create all tables in the database."""
    logging.info("Initializing database.")
    parsed_uri = urlparse(SQLALCHEMY_DATABASE_URI)
    db_name = parsed_uri.path[1:]  # Strip leading slash to get the database name
    logging.info(f"Connecting to database: {db_name}")
    Base.metadata.create_all(bind=engine)
