from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from rich.logging import RichHandler

from .config import Settings, load_settings
from .handlers import build_router
from .middlewares import DependencyMiddleware
from .services import (
    DeepgramModelPreferences,
    DeepgramTranscriber,
    GroqTranscriber,
    TelethonDownloadService,
    TranscriberRegistry,
    ProviderPreferences,
)
from .services.audio_optimizer import AudioOptimizer, TranscriptCache
from .services.queue_service import TaskQueue

LOG_FORMAT = "%(message)s"


async def run_bot() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt="%H:%M:%S",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    )
    settings = load_settings()

    bot = Bot(settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(build_router())

    registry = _build_registry(settings)
    preferences = ProviderPreferences(default=registry.default_provider)
    deepgram_models = DeepgramModelPreferences(settings.deepgram_default_model)
    telethon_downloader = TelethonDownloadService(
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
        bot_token=settings.telegram_bot_token,
    )

    # Initialize optimization components
    logger = logging.getLogger(__name__)

    # Audio Optimizer
    audio_optimizer = AudioOptimizer(
        target_bitrate=settings.audio_target_bitrate,
        target_sample_rate=settings.audio_target_sample_rate,
        target_channels=settings.audio_target_channels,
        use_streaming=settings.audio_use_streaming,
    )
    logger.info(
        "Audio Optimizer initialized (streaming: %s, bitrate: %s, threshold: %dMB)",
        settings.audio_use_streaming,
        settings.audio_target_bitrate,
        settings.audio_compression_threshold_mb,
    )

    # Transcript Cache
    transcript_cache = None
    if settings.cache_enabled:
        if settings.cache_type == "redis" and settings.redis_url:
            logger.info("Redis cache not yet implemented, using memory cache")
            transcript_cache = TranscriptCache(max_size=settings.cache_max_size)
        else:
            transcript_cache = TranscriptCache(max_size=settings.cache_max_size)
        logger.info(
            "Transcript cache enabled (type: %s, max_size: %d)",
            settings.cache_type,
            settings.cache_max_size,
        )

    # Task Queue
    task_queue = TaskQueue(
        max_workers=settings.queue_max_workers,
        max_retries=settings.queue_max_retries,
        retry_delay=settings.queue_retry_delay,
        rate_limit_per_user=settings.queue_rate_limit_per_user,
    )
    await task_queue.start()
    logger.info(
        "Task queue started (workers: %d, rate_limit: %d per user)",
        settings.queue_max_workers,
        settings.queue_rate_limit_per_user,
    )

    dependency_middleware = DependencyMiddleware(
        transcriber_registry=registry,
        provider_preferences=preferences,
        telethon_downloader=telethon_downloader,
        deepgram_model_preferences=deepgram_models,
        audio_optimizer=audio_optimizer,
        transcript_cache=transcript_cache,
        task_queue=task_queue,
        compression_threshold_mb=settings.audio_compression_threshold_mb,
    )
    dispatcher.message.middleware.register(dependency_middleware)
    dispatcher.callback_query.middleware.register(dependency_middleware)

    # Check webhook mode
    if settings.webhook_url:
        logger.info("Webhook mode detected but not yet fully implemented")
        logger.info("Falling back to polling mode")
        logger.info("To use webhook, see app/webhook.py for implementation")

    try:
        logger.info("🚀 Bot started with optimizations enabled!")
        logger.info(
            "📊 Features: Caching=%s, Queue=%d workers, Streaming=%s",
            settings.cache_enabled,
            settings.queue_max_workers,
            settings.audio_use_streaming,
        )
        await dispatcher.start_polling(bot)
    finally:
        logger.info("Shutting down...")
        await task_queue.stop()
        logger.info("Task queue stopped")

        # Cleanup Telethon session
        await telethon_downloader.close()
        logger.info("Telethon session closed")


def _build_registry(settings: Settings) -> TranscriberRegistry:
    transcribers: dict[str, object] = {}
    if settings.groq_api_key:
        transcribers["groq"] = GroqTranscriber(settings.groq_api_key)
    if settings.deepgram_api_key:
        transcribers["deepgram"] = DeepgramTranscriber(
            settings.deepgram_api_key,
            model=settings.deepgram_default_model,
            detect_language=settings.deepgram_detect_language,
        )

    if not transcribers:
        raise RuntimeError(
            "Tidak ada transcriber yang dikonfigurasi. Tambahkan GROQ_API_KEY atau DEEPGRAM_API_KEY."
        )

    default = (
        settings.transcription_provider
        if settings.transcription_provider in transcribers
        else next(iter(transcribers))
    )
    return TranscriberRegistry(default, transcribers)


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
