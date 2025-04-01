from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_MODEL_ID: str = os.getenv("OPENAI_MODEL_ID")

settings = Settings()