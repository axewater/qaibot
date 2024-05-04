from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
from .config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()

class BotStatistics(Base):
    __tablename__ = 'bot_statistics'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    date_first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    settings = relationship("UserSetting", back_populates="user")
    logs = relationship("Log", back_populates="user")

class UserSetting(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    setting_name = Column(String)
    setting_value = Column(String)
    user = relationship("User", back_populates="settings")

class AdminSetting(Base):
    __tablename__ = 'admin_settings'
    id = Column(Integer, primary_key=True)
    setting_name = Column(String)
    setting_value = Column(Boolean)

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message = Column(String)
    user = relationship("User", back_populates="logs")

# Setup the engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
