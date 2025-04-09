import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_MODEL_ID: str = st.secrets.OPENAI_MODEL_ID
    OPENAI_API_KEY: str = st.secrets.OPENAI_API_KEY

settings = Settings()