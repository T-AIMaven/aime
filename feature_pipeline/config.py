from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_MODEL_ID: str = st.secrets.OPENAI_MODEL_ID
    DB_PATH: str = st.secrets.DB_PATH
    DATASET_FILE: str = st.secrets.DATASET_FILE
    TOP_K: int = st.secrets.TOP_K

settings = Settings()