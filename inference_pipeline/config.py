from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_MODEL_ID: str = os.getenv("OPENAI_MODEL_ID")
    DATASET_FILE: str = os.getenv("DATASET_FILE")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
settings = Settings()