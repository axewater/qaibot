# bot/models.py
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class BotStatistics(Base):
    __tablename__ = 'bot_statistics'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(String)
    last_registered_version = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    date_first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    user_discord_id = Column(BigInteger, unique=True, nullable=True)
    settings = relationship("UserSetting", back_populates="user")
    log_entries = relationship("Log", back_populates="user")
    message_logs = relationship("MessageLog", back_populates="user")

class UserSetting(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    setting_name = Column(String)
    setting_value = Column(String)
    learn_about_me = Column(Boolean, default=True)
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
    user = relationship("User", back_populates="log_entries")

class MessageLog(Base):
    __tablename__ = 'message_logs'
    id = Column(Integer, primary_key=True)
    server_id = Column(String)
    server_name = Column(String)
    channel_id = Column(String)
    channel_name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    message_content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="message_logs")
