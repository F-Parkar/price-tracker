import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')

    DATABASE_PATH = 'price_tracker.db'

    GMAIL_USER = os.environ.get('GMAIL_USER')
    GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')

    # Price checking interval in seconds (3600 = 1 hour)
    CHECK_INTERVAL = 3600