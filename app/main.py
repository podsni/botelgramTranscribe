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

    transcriber = _build_transcriber(settings)
    telethon_downloader = TelethonDownloadService(
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
        bot_token=settings.telegram_bot_token,
    )

    dependency_middleware = DependencyMiddleware(
        transcriber=transcriber,
        telethon_downloader=telethon_downloader,
    )
    dispatcher.message.middleware.register(dependency_middleware)

    await dispatcher.start_polling(bot)


def _build_transcriber(settings: Settings):
    if settings.transcription_provider == "deepgram":
        assert settings.deepgram_api_key  # Guarded during settings load
        return DeepgramTranscriber(settings.deepgram_api_key)
    assert settings.groq_api_key  # Guarded during settings load
    return GroqTranscriber(settings.groq_api_key)


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
