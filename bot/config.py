# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
MOBYGAMES_API_KEY = os.getenv('MOBYGAMES_API_KEY')
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY')
QAI_VERSION = '3.2.2'
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:!Piratingin2024!@theknox:5432/qaibot_noenv')
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
DISCORD_ADMIN_ROLENAME = os.getenv('DISCORD_ADMIN_ROLENAME', 'qbotadmins')
