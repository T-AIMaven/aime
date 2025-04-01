from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()
class Settings:
    OPENAI_MODEL_ID: str = os.getenv("OPENAI_MODEL_ID")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
settings = Settings()
