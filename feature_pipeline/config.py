from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_MODEL_ID: str = os.getenv("OPENAI_MODEL_ID")
    DB_PATH: str = os.getenv("DB_PATH")
    DATASET_FILE: str = os.getenv("DATASET_FILE")
    TOP_K: int = os.getenv("TOP_K")

settings = Settings()