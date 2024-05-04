from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import SQLALCHEMY_DATABASE_URI
import datetime

Base = declarative_base()

class BotStatistics(Base):
    __tablename__ = 'bot_statistics'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(String)

# Setup the engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)