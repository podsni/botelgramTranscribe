import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    groq_api_key: str


def load_settings() -> Settings:
    # Allow .env usage for local development while still respecting env vars.
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    groq_key = os.getenv("GROQ_API_KEY")

    if not telegram_token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in environment or .env file.")
    if not groq_key:
        raise RuntimeError("Missing GROQ_API_KEY in environment or .env file.")

    return Settings(telegram_bot_token=telegram_token, groq_api_key=groq_key)
