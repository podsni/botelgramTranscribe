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
    deepgram_detect_language: bool

    # Optimization settings
    cache_enabled: bool
    cache_type: str
    cache_max_size: int
    cache_ttl: int
    redis_url: Optional[str]

    queue_max_workers: int
    queue_max_retries: int
    queue_retry_delay: int
    queue_rate_limit_per_user: int

    audio_use_streaming: bool
    audio_target_bitrate: str
    audio_target_sample_rate: int
    audio_target_channels: int
    audio_compression_threshold_mb: int

    webhook_url: Optional[str]
    webhook_path: str
    webhook_port: int
    webhook_secret: Optional[str]


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
    deepgram_detect_language_raw = (
        (os.getenv("DEEPGRAM_DETECT_LANGUAGE") or "true").strip().lower()
    )

    if not telegram_token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in environment or .env file.")
    if not api_id:
        raise RuntimeError("Missing TELEGRAM_API_ID in environment or .env file.")
    if not api_hash:
        raise RuntimeError("Missing TELEGRAM_API_HASH in environment or .env file.")
    if provider not in {"groq", "deepgram"}:
        raise RuntimeError(
            "TRANSCRIPTION_PROVIDER must be either 'groq' or 'deepgram'."
        )
    if provider == "groq" and not groq_key:
        raise RuntimeError("Missing GROQ_API_KEY for Groq transcription provider.")
    if provider == "deepgram" and not deepgram_key:
        raise RuntimeError(
            "Missing DEEPGRAM_API_KEY for Deepgram transcription provider."
        )

    try:
        api_id_int = int(api_id)
    except ValueError as exc:
        raise RuntimeError("TELEGRAM_API_ID must be an integer.") from exc

    if provider == "deepgram" and deepgram_model not in {"whisper", "nova-3"}:
        raise RuntimeError("DEEPGRAM_MODEL must be 'whisper' or 'nova-3'.")
    if deepgram_key and deepgram_model not in {"whisper", "nova-3"}:
        raise RuntimeError("DEEPGRAM_MODEL must be 'whisper' or 'nova-3'.")

    detect_language = deepgram_detect_language_raw in {"1", "true", "yes", "on"}

    # Optimization settings with defaults
    cache_enabled = os.getenv("CACHE_ENABLED", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    cache_type = os.getenv("CACHE_TYPE", "memory").strip().lower()
    cache_max_size = int(os.getenv("CACHE_MAX_SIZE", "100"))
    cache_ttl = int(os.getenv("CACHE_TTL", "604800"))  # 7 days
    redis_url = os.getenv("REDIS_URL")

    queue_max_workers = int(os.getenv("QUEUE_MAX_WORKERS", "5"))
    queue_max_retries = int(os.getenv("QUEUE_MAX_RETRIES", "2"))
    queue_retry_delay = int(os.getenv("QUEUE_RETRY_DELAY", "5"))
    queue_rate_limit = int(os.getenv("QUEUE_RATE_LIMIT_PER_USER", "3"))

    audio_streaming = os.getenv("AUDIO_USE_STREAMING", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    audio_bitrate = os.getenv("AUDIO_TARGET_BITRATE", "96k").strip()
    audio_sample_rate = int(os.getenv("AUDIO_TARGET_SAMPLE_RATE", "16000"))
    audio_channels = int(os.getenv("AUDIO_TARGET_CHANNELS", "1"))
    audio_threshold = int(os.getenv("AUDIO_COMPRESSION_THRESHOLD_MB", "30"))

    webhook_url = os.getenv("WEBHOOK_URL")
    webhook_path = os.getenv("WEBHOOK_PATH", "/webhook").strip()
    webhook_port = int(os.getenv("WEBHOOK_PORT", "8080"))
    webhook_secret = os.getenv("WEBHOOK_SECRET")

    return Settings(
        telegram_bot_token=telegram_token,
        telegram_api_id=api_id_int,
        telegram_api_hash=api_hash,
        groq_api_key=groq_key,
        deepgram_api_key=deepgram_key,
        transcription_provider=provider,
        deepgram_default_model=deepgram_model,
        deepgram_detect_language=detect_language,
        cache_enabled=cache_enabled,
        cache_type=cache_type,
        cache_max_size=cache_max_size,
        cache_ttl=cache_ttl,
        redis_url=redis_url,
        queue_max_workers=queue_max_workers,
        queue_max_retries=queue_max_retries,
        queue_retry_delay=queue_retry_delay,
        queue_rate_limit_per_user=queue_rate_limit,
        audio_use_streaming=audio_streaming,
        audio_target_bitrate=audio_bitrate,
        audio_target_sample_rate=audio_sample_rate,
        audio_target_channels=audio_channels,
        audio_compression_threshold_mb=audio_threshold,
        webhook_url=webhook_url,
        webhook_path=webhook_path,
        webhook_port=webhook_port,
        webhook_secret=webhook_secret,
    )
