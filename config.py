import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_URL = os.getenv("DB_KEY")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GEMINI_KEY = os.getenv("GEMINI_KEY")
    VT_KEY = os.getenv("VT_KEY")

