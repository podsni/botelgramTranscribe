from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from rich.logging import RichHandler

from .config import Settings, load_settings
from .handlers import build_router
from .middlewares import DependencyMiddleware
from .services import (
    DeepgramTranscriber,
    GroqTranscriber,
    TelethonDownloadService,
    TranscriberRegistry,
    ProviderPreferences,
)

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
    telethon_downloader = TelethonDownloadService(
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
        bot_token=settings.telegram_bot_token,
    )

    dependency_middleware = DependencyMiddleware(
        transcriber_registry=registry,
        provider_preferences=preferences,
        telethon_downloader=telethon_downloader,
    )
    dispatcher.message.middleware.register(dependency_middleware)
    dispatcher.callback_query.middleware.register(dependency_middleware)

    await dispatcher.start_polling(bot)


def _build_registry(settings: Settings) -> TranscriberRegistry:
    transcribers: dict[str, object] = {}
    if settings.groq_api_key:
        transcribers["groq"] = GroqTranscriber(settings.groq_api_key)
    if settings.deepgram_api_key:
        transcribers["deepgram"] = DeepgramTranscriber(settings.deepgram_api_key)

    if not transcribers:
        raise RuntimeError("Tidak ada transcriber yang dikonfigurasi. Tambahkan GROQ_API_KEY atau DEEPGRAM_API_KEY.")

    default = settings.transcription_provider if settings.transcription_provider in transcribers else next(iter(transcribers))
    return TranscriberRegistry(default, transcribers)


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
