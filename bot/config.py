# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

QAI_VERSION = '3.4.3'
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:!Piratingin2024!@theknox:5432/qaibot_noenv')
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5678))
SECRET_KEY = os.getenv('SECRET_KEY')
DISCORD_ADMIN_ROLENAME = os.getenv('DISCORD_ADMIN_ROLENAME', 'qbotadmins')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
MOBYGAMES_API_KEY = os.getenv('MOBYGAMES_API_KEY')
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY')
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
SHODAN_API_KEY = os.getenv('SHODAN_API_KEY')

# eBay API credentials
EBAY_APP_ID = os.getenv('EBAY_APP_ID')
EBAY_DEV_ID = os.getenv('EBAY_DEV_ID')
EBAY_CERT_ID = os.getenv('EBAY_CERT_ID')
