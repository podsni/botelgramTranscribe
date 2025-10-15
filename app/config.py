import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_api_id: int
    telegram_api_hash: str
    groq_api_key: Optional[str]
    deepgram_api_key: Optional[str]
    transcription_provider: str
    deepgram_default_model: str


def load_settings() -> Settings:
    # Allow .env usage for local development while still respecting env vars.
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    groq_key = os.getenv("GROQ_API_KEY")
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    provider = (os.getenv("TRANSCRIPTION_PROVIDER") or "groq").strip().lower()
    deepgram_model = (os.getenv("DEEPGRAM_MODEL") or "whisper").strip().lower()

    if not telegram_token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in environment or .env file.")
    if not api_id:
        raise RuntimeError("Missing TELEGRAM_API_ID in environment or .env file.")
    if not api_hash:
        raise RuntimeError("Missing TELEGRAM_API_HASH in environment or .env file.")
    if provider not in {"groq", "deepgram"}:
        raise RuntimeError("TRANSCRIPTION_PROVIDER must be either 'groq' or 'deepgram'.")
    if provider == "groq" and not groq_key:
        raise RuntimeError("Missing GROQ_API_KEY for Groq transcription provider.")
    if provider == "deepgram" and not deepgram_key:
        raise RuntimeError("Missing DEEPGRAM_API_KEY for Deepgram transcription provider.")

    try:
        api_id_int = int(api_id)
    except ValueError as exc:
        raise RuntimeError("TELEGRAM_API_ID must be an integer.") from exc

    if provider == "deepgram" and deepgram_model not in {"whisper", "nova-3"}:
        raise RuntimeError("DEEPGRAM_MODEL must be 'whisper' or 'nova-3'.")
    if deepgram_key and deepgram_model not in {"whisper", "nova-3"}:
        raise RuntimeError("DEEPGRAM_MODEL must be 'whisper' or 'nova-3'.")

    return Settings(
        telegram_bot_token=telegram_token,
        telegram_api_id=api_id_int,
        telegram_api_hash=api_hash,
        groq_api_key=groq_key,
        deepgram_api_key=deepgram_key,
        transcription_provider=provider,
        deepgram_default_model=deepgram_model,
    )
