from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional

from telethon import TelegramClient
from telethon.errors import FloodWaitError, RPCError, SessionPasswordNeededError
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[int, int], None]]


class TelethonDownloadService:
    """
    Acquire media via MTProto with persistent session to avoid FloodWait errors.
    """

    def __init__(self, api_id: int, api_hash: str, bot_token: str) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self._lock = asyncio.Lock()
        self._client: Optional[TelegramClient] = None
        self._session_string: Optional[str] = None
        self._session_file = Path.home() / ".transhades_session"

    async def _get_client(self) -> TelegramClient:
        """Get or create persistent Telegram client."""
        if self._client and self._client.is_connected():
            return self._client

        # Load session from file if exists
        if self._session_file.exists():
            try:
                self._session_string = self._session_file.read_text().strip()
                logger.info("Loaded existing Telegram session")
            except Exception as e:
                logger.warning("Failed to load session file: %s", e)
                self._session_string = None

        # Create client with session
        session = (
            StringSession(self._session_string)
            if self._session_string
            else StringSession()
        )
        self._client = TelegramClient(
            session=session,
            api_id=self.api_id,
            api_hash=self.api_hash,
        )

        await self._client.connect()

        # Authorize if needed
        if not await self._client.is_user_authorized():
            logger.info("Authorizing bot with Telegram...")
            try:
                await self._client.sign_in(bot_token=self.bot_token)

                # Save session for next time
                session_str = self._client.session.save()
                self._session_file.write_text(session_str)
                self._session_file.chmod(0o600)  # Read/write for owner only
                logger.info("Telegram session saved successfully")

            except SessionPasswordNeededError as exc:
                await self._client.disconnect()
                raise RuntimeError(
                    "Autentikasi bot membutuhkan password tambahan."
                ) from exc

        return self._client

    async def download_media(
        self,
        chat_id: int,
        message_id: int,
        file_path: str,
        progress_callback: ProgressCallback = None,
        max_retries: int = 3,
    ) -> None:
        """
        Download media with FloodWait handling and retry logic.

        Args:
            chat_id: Telegram chat ID
            message_id: Message ID containing media
            file_path: Destination file path
            progress_callback: Optional progress callback
            max_retries: Maximum retry attempts for transient errors
        """
        async with self._lock:
            for attempt in range(max_retries):
                try:
                    client = await self._get_client()

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

                    logger.info("Media downloaded successfully to %s", file_path)
                    return

                except FloodWaitError as flood_err:
                    wait_time = flood_err.seconds

                    # If this is during initial auth, try to use existing session
                    if attempt == 0 and self._session_file.exists():
                        logger.warning(
                            "FloodWait during auth (%d seconds). "
                            "This means Telegram rate limit is still active from previous sessions. "
                            "Bot will continue with limited functionality.",
                            wait_time,
                        )
                        # Don't raise immediately, let cache handle duplicates
                        raise RuntimeError(
                            f"⏳ Telegram sedang membatasi download baru (rate limit aktif).\n\n"
                            f"**File duplikat tetap bisa diproses dari cache!**\n"
                            f"Untuk file baru, silakan tunggu ~{wait_time // 60} menit.\n\n"
                            f"💡 Bot akan tetap berjalan dan melayani file yang sudah pernah di-upload."
                        ) from flood_err

                    logger.warning(
                        "FloodWait: Telegram requires waiting %d seconds. "
                        "This is normal for rate limiting.",
                        wait_time,
                    )

                    # If wait time is reasonable, wait and retry
                    if wait_time <= 120:  # Max 2 minutes wait
                        logger.info("Waiting %d seconds before retry...", wait_time)
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        # Too long to wait, raise error but bot continues
                        raise RuntimeError(
                            f"⏳ Telegram FloodWait aktif.\n\n"
                            f"**File yang sudah pernah di-upload tetap bisa diproses dari cache!**\n"
                            f"File baru perlu tunggu ~{wait_time // 60} menit.\n\n"
                            f"💡 Kirim ulang file lama untuk instant result dari cache!"
                        ) from flood_err

                except RPCError as exc:
                    if attempt < max_retries - 1:
                        logger.warning(
                            "RPC error on attempt %d/%d: %s. Retrying...",
                            attempt + 1,
                            max_retries,
                            exc,
                        )
                        await asyncio.sleep(2**attempt)  # Exponential backoff

                        # Disconnect and reconnect for next attempt
                        if self._client:
                            await self._client.disconnect()
                            self._client = None
                        continue
                    else:
                        raise RuntimeError(
                            f"Gagal mengambil media melalui MTProto setelah {max_retries} percobaan: {exc}"
                        ) from exc

                except Exception as exc:
                    logger.exception("Unexpected error during media download")
                    raise RuntimeError(f"Error downloading media: {exc}") from exc

    async def close(self) -> None:
        """Close Telegram client connection."""
        if self._client and self._client.is_connected():
            await self._client.disconnect()
            logger.info("Telegram client disconnected")

    async def get_file_unique_id(self, chat_id: int, message_id: int) -> Optional[str]:
        """
        Get unique file ID from Telegram message without downloading.
        Useful for duplicate detection before download.

        Args:
            chat_id: Telegram chat ID
            message_id: Message ID containing media

        Returns:
            Unique file ID string or None if no media
        """
        async with self._lock:
            try:
                client = await self._get_client()
                entity = await client.get_entity(chat_id)
                telegram_message = await client.get_messages(entity, ids=message_id)

                if not telegram_message or not telegram_message.media:
                    return None

                # Get unique file ID from media
                if hasattr(telegram_message.media, "document"):
                    # For documents, videos, audio
                    doc = telegram_message.media.document
                    return f"{doc.id}_{doc.access_hash}"
                elif hasattr(telegram_message.media, "photo"):
                    # For photos
                    photo = telegram_message.media.photo
                    return f"{photo.id}_{photo.access_hash}"

                return None

            except Exception as e:
                logger.warning("Failed to get file unique ID: %s", e)
                return None
