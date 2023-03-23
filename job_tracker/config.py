import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_BASE_URL = os.getenv("API_BASE_URL")
    API_USER = os.getenv("API_USER")
    API_KEY = os.getenv("API_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
