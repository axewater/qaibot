# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')
MOBYGAMES_API_KEY = os.getenv('MOBYGAMES_API_KEY')
QAI_VERSION = '2.1.6'
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:!Piratingin2024!@theknox:5432/qaibot_noenv')