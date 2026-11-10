import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    database_url: str

def get_setting() -> Settings:
    return Settings(
        openai_api_key = os.getenv("OPENAI_API_KEY"),
        openai_model = os.getenv("OPENAI_MODEL"),
        database_url = os.getenv("DATABASE_URL")
    )