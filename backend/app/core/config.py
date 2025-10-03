import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the `backend` directory
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings()