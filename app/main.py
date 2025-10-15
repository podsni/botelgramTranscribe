from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from telethon import TelegramClient

from .config import Settings, load_settings
from .handlers import build_router
from .middlewares import DependencyMiddleware
from .services import GroqTranscriber

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s | %(message)s"


async def create_telethon_client(settings: Settings) -> TelegramClient:
    client = TelegramClient(
        session="transhades_bot",
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
    )
    await client.start(bot_token=settings.telegram_bot_token)
    return client


async def run_bot() -> None:
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    settings = load_settings()

    bot = Bot(settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(build_router())

    transcriber = GroqTranscriber(settings.groq_api_key)
    telethon_client = await create_telethon_client(settings)

    dependency_middleware = DependencyMiddleware(
        transcriber=transcriber,
        telethon_client=telethon_client,
    )
    dispatcher.message.middleware.register(dependency_middleware)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await telethon_client.disconnect()


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
