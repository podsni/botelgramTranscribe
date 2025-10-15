from __future__ import annotations

import asyncio
from typing import Callable, Optional

from telethon import TelegramClient
from telethon.errors import RPCError, SessionPasswordNeededError
from telethon.sessions import MemorySession


ProgressCallback = Optional[Callable[[int, int], None]]


class TelethonDownloadService:
    """Acquire media via MTProto on-demand to avoid long-running session conflicts."""

    def __init__(self, api_id: int, api_hash: str, bot_token: str) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self._lock = asyncio.Lock()

    async def download_media(
        self,
        chat_id: int,
        message_id: int,
        file_path: str,
        progress_callback: ProgressCallback = None,
    ) -> None:
        async with self._lock:
            client = TelegramClient(
                session=MemorySession(),
                api_id=self.api_id,
                api_hash=self.api_hash,
            )
            await client.connect()
            try:
                if not await client.is_user_authorized():
                    await client.sign_in(bot_token=self.bot_token)
            except SessionPasswordNeededError as exc:
                await client.disconnect()
                raise RuntimeError("Autentikasi bot membutuhkan password tambahan.") from exc

            try:
                entity = await client.get_entity(chat_id)
                telegram_message = await client.get_messages(entity, ids=message_id)

                if not telegram_message:
                    raise RuntimeError("Tidak menemukan media pada pesan tersebut.")

                result = await client.download_media(
                    telegram_message,
                    file=file_path,
                    progress_callback=progress_callback,
                )
                if not result:
                    raise RuntimeError("Download media melalui Telethon gagal.")
            except RPCError as exc:
                raise RuntimeError(f"Gagal mengambil media melalui MTProto: {exc}") from exc
            finally:
                await client.disconnect()
