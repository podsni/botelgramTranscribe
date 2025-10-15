from __future__ import annotations

import asyncio
import io
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import requests
from telegram import InputFile, Update
from telegram.constants import ChatAction
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from .services import GroqTranscriber, TranscriptionResult

logger = logging.getLogger(__name__)

TELEGRAM_FILE_DOWNLOAD_LIMIT = 20 * 1024 * 1024  # Telegram Bot API max downloadable size.
TELEGRAM_MESSAGE_LIMIT = 4000
AUDIO_CONVERSION_THRESHOLD = 15 * 1024 * 1024  # Convert to mp3 when file size >= 15MB.


class TelegramBotHandlers:
    """Collection of Telegram handlers that orchestrate transcription."""

    def __init__(self, transcriber: GroqTranscriber) -> None:
        self.transcriber = transcriber

    @staticmethod
    def _pick_media(message) -> Optional[Tuple[object, str]]:
        if message.voice:
            return message.voice, ".ogg"
        if message.audio:
            return message.audio, ".mp3"
        if message.video:
            return message.video, ".mp4"
        if message.video_note:
            return message.video_note, ".mp4"
        if message.document and message.document.mime_type:
            if message.document.mime_type.startswith("audio"):
                return message.document, ".mp3"
            if message.document.mime_type.startswith("video"):
                return message.document, ".mp4"
        return None

    @staticmethod
    def _build_temp_file(meta: object, fallback_suffix: str) -> Tuple[Path, str]:
        file_name = getattr(meta, "file_name", None) or f"telegram_media{fallback_suffix}"
        suffix = Path(file_name).suffix or fallback_suffix
        temp_dir = Path(tempfile.mkdtemp(prefix="transhades_"))
        return temp_dir / f"input{suffix}", file_name

    @staticmethod
    def _chunk_text(message: str, limit: int) -> list[str]:
        return [message[i : i + limit] for i in range(0, len(message), limit)]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.effective_message.reply_text(
            "Kirim atau forward file audio, voice note, atau video ke bot ini. "
            "Bot akan mengirimkan transkrip menggunakan Groq Whisper."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.effective_message.reply_text(
            "Gunakan bot ini dengan mengirimkan atau mem-forward audio (mp3/m4a/ogg) "
            "atau video (mp4). Bot akan mengembalikan teks hasil transkripsinya."
        )

    async def handle_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.effective_message
        media = self._pick_media(message)
        if not media:
            await message.reply_text("Format file tidak dikenali. Kirim audio, voice note, atau video.")
            return

        meta, fallback_suffix = media
        file_size = getattr(meta, "file_size", None)
        if file_size:
            logger.info(
                "Receiving media %s (%s bytes) for chat %s",
                getattr(meta, "file_name", "unknown"),
                file_size,
                message.chat_id,
            )

        await context.bot.send_chat_action(chat_id=message.chat_id, action=ChatAction.TYPING)

        file_path, original_name = self._build_temp_file(meta, fallback_suffix)
        cleanup_paths = {file_path}
        try:
            telegram_file = await context.bot.get_file(meta.file_id)
            await telegram_file.download_to_drive(custom_path=str(file_path))
            logger.info("Downloaded %s to %s", original_name, file_path)

            prepared_path = await asyncio.to_thread(
                self._prepare_audio_for_transcription,
                file_path,
                file_size,
            )
            if prepared_path != file_path:
                cleanup_paths.add(prepared_path)

            result = await asyncio.to_thread(self.transcriber.transcribe, prepared_path)
            await self._deliver_transcription(message, result)
        except BadRequest as bad_request:
            logger.exception("Telegram refused to provide file: %s", bad_request)
            await message.reply_text(
                "Telegram menolak memberikan file (kemungkinan karena ukuran >20MB). "
                "Silakan kompres file atau potong menjadi bagian lebih kecil sebelum dikirim ulang."
            )
        except requests.HTTPError:
            logger.exception("Groq API returned an error response")
            await message.reply_text(
                "Terjadi kesalahan dari Groq API saat memproses file. "
                "Silakan coba lagi nanti."
            )
        except subprocess.CalledProcessError:
            logger.exception("Failed to convert media to mp3")
            await message.reply_text(
                "Gagal mengonversi media ke format mp3. Pastikan ffmpeg terpasang di server."
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to process media")
            await message.reply_text(f"Gagal memproses file: {exc}")
        finally:
            try:
                for path in cleanup_paths:
                    if path.exists():
                        path.unlink()
                if file_path.parent.exists():
                    file_path.parent.rmdir()
            except OSError:
                logger.warning(
                    "Failed to clean temp directory %s", file_path.parent, exc_info=True
                )

    @staticmethod
    def _prepare_audio_for_transcription(source_path: Path, file_size: Optional[int]) -> Path:
        if file_size is None:
            logger.info("Skipping conversion for %s (ukuran tidak diketahui).", source_path)
            return source_path

        if file_size < AUDIO_CONVERSION_THRESHOLD:
            logger.info(
                "Skipping conversion for %s (size %s bytes below threshold).",
                source_path,
                file_size,
            )
            return source_path

        target_path = source_path.with_suffix(".mp3")
        logger.info(
            "Converting %s (%s bytes) to mp3 at %s",
            source_path,
            file_size,
            target_path,
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(source_path),
                "-vn",
                "-acodec",
                "mp3",
                str(target_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info("Conversion complete for %s", target_path)
        return target_path

    async def _deliver_transcription(self, message, result: TranscriptionResult) -> None:
        plain_text = result.to_plain_text()
        if not plain_text:
            await message.reply_text("Transkrip kosong diterima dari Groq.")
            return

        if len(plain_text) <= TELEGRAM_MESSAGE_LIMIT:
            await message.reply_text(plain_text)
        else:
            preview = plain_text[:TELEGRAM_MESSAGE_LIMIT]
            await message.reply_text(
                preview + "\n\n[Transkrip dipotong. Versi lengkap tersedia di lampiran.]"
            )

        await self._send_transcript_files(message, result, plain_text)

    async def _send_transcript_files(
        self,
        message,
        result: TranscriptionResult,
        plain_text: str,
    ) -> None:
        txt_buffer = io.BytesIO(plain_text.encode("utf-8"))
        txt_buffer.name = "transcript.txt"
        await message.reply_document(
            document=InputFile(txt_buffer, filename="transcript.txt"),
            caption="Transkrip teks tanpa timestamp.",
        )

        try:
            if result.segments:
                srt_content = result.to_srt()
                if srt_content:
                    srt_buffer = io.BytesIO(srt_content.encode("utf-8"))
                    srt_buffer.name = "transcript.srt"
                    await message.reply_document(
                        document=InputFile(srt_buffer, filename="transcript.srt"),
                        caption="Transkrip format SRT.",
                    )
        except ValueError:
            logger.info("SRT output tidak tersedia karena segment informasi tidak lengkap.")
