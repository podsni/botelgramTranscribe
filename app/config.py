import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_api_id: int
    telegram_api_hash: str
    groq_api_key: str


def load_settings() -> Settings:
    # Allow .env usage for local development while still respecting env vars.
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    groq_key = os.getenv("GROQ_API_KEY")

    if not telegram_token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in environment or .env file.")
    if not api_id:
        raise RuntimeError("Missing TELEGRAM_API_ID in environment or .env file.")
    if not api_hash:
        raise RuntimeError("Missing TELEGRAM_API_HASH in environment or .env file.")
    if not groq_key:
        raise RuntimeError("Missing GROQ_API_KEY in environment or .env file.")

    try:
        api_id_int = int(api_id)
    except ValueError as exc:
        raise RuntimeError("TELEGRAM_API_ID must be an integer.") from exc

    return Settings(
        telegram_bot_token=telegram_token,
        telegram_api_id=api_id_int,
        telegram_api_hash=api_hash,
        groq_api_key=groq_key,
    )
