import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    MODEL_NAME = "openai/gpt-oss-20b"

    TEMPERATURE = 0.3

    MAX_TOKENS = 300