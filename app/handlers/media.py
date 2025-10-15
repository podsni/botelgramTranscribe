from __future__ import annotations

import asyncio
import io
import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.chat_action import ChatActionSender
from telethon import TelegramClient
from telethon.errors import RPCError

from ..services import GroqTranscriber, TranscriptionResult

logger = logging.getLogger(__name__)

router = Router()

TELEGRAM_FILE_DOWNLOAD_LIMIT = 2 * 1024 * 1024 * 1024  # 2 GB via MTProto.
TELEGRAM_MESSAGE_LIMIT = 4000
AUDIO_CONVERSION_THRESHOLD = 15 * 1024 * 1024  # Convert to mp3 when file size >= 15MB.


@dataclass
class MediaMeta:
    display_name: str
    suffix: str
    file_size: Optional[int]


@router.message()
async def handle_media(
    message: Message,
    telethon_client: TelegramClient,
    transcriber: GroqTranscriber,
) -> None:
    meta = _pick_media(message)
    if not meta:
        return

    if meta.file_size and meta.file_size > TELEGRAM_FILE_DOWNLOAD_LIMIT:
        await message.answer(
            "Ukuran file melebihi 2GB sehingga tidak bisa diunduh. "
            "Silakan kompres atau bagi menjadi beberapa bagian terlebih dahulu."
        )
        return

    temp_file, temp_dir = _build_temp_file(meta)
    cleanup_paths = {temp_file}

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            await _download_media(telethon_client, message, temp_file)
            logger.info("Downloaded media to %s", temp_file)

            prepared_path = await asyncio.to_thread(
                _prepare_audio_for_transcription,
                temp_file,
                meta.file_size,
            )
            if prepared_path != temp_file:
                cleanup_paths.add(prepared_path)

            result = await asyncio.to_thread(transcriber.transcribe, prepared_path)
            await _deliver_transcription(message, result)
        except RPCError as rpc_error:
            logger.exception("Telethon failed to fetch media")
            await message.answer(
                f"Gagal mengambil media melalui MTProto: {rpc_error}. "
                "Pastikan bot memiliki akses ke percakapan ini."
            )
        except subprocess.CalledProcessError:
            logger.exception("Failed to convert media to mp3 via ffmpeg")
            await message.answer(
                "Gagal mengonversi media ke format mp3. Pastikan ffmpeg terpasang pada server."
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unhandled error while processing media")
            await message.answer(f"Gagal memproses file: {exc}")
        finally:
            for path in cleanup_paths:
                try:
                    if path.exists():
                        path.unlink()
                except OSError:
                    logger.warning("Failed to delete temporary file %s", path, exc_info=True)
            try:
                temp_dir.rmdir()
            except OSError:
                logger.warning("Failed to remove temporary directory %s", temp_dir, exc_info=True)


def _pick_media(message: Message) -> Optional[MediaMeta]:
    if message.voice:
        return MediaMeta(
            display_name="voice_note.ogg",
            suffix=".ogg",
            file_size=message.voice.file_size,
        )
    if message.audio:
        suffix = Path(message.audio.file_name or "audio.mp3").suffix or ".mp3"
        return MediaMeta(
            display_name=message.audio.file_name or f"audio{suffix}",
            suffix=suffix,
            file_size=message.audio.file_size,
        )
    if message.video:
        suffix = Path(message.video.file_name or "video.mp4").suffix or ".mp4"
        return MediaMeta(
            display_name=message.video.file_name or f"video{suffix}",
            suffix=suffix,
            file_size=message.video.file_size,
        )
    if message.video_note:
        return MediaMeta(
            display_name="video_note.mp4",
            suffix=".mp4",
            file_size=message.video_note.file_size,
        )
    if message.document and message.document.mime_type:
        mime = message.document.mime_type
        if mime.startswith("audio") or mime.startswith("video"):
            suffix = Path(message.document.file_name or "media").suffix
            fallback_suffix = ".mp3" if mime.startswith("audio") else ".mp4"
            return MediaMeta(
                display_name=message.document.file_name or f"media{fallback_suffix}",
                suffix=suffix or fallback_suffix,
                file_size=message.document.file_size,
            )
    return None


def _build_temp_file(meta: MediaMeta) -> tuple[Path, Path]:
    temp_dir = Path(tempfile.mkdtemp(prefix="transhades_"))
    suffix = meta.suffix or ".bin"
    temp_file = temp_dir / f"input{suffix}"
    return temp_file, temp_dir


async def _download_media(
    telethon_client: TelegramClient,
    message: Message,
    target_path: Path,
) -> None:
    entity = await telethon_client.get_entity(message.chat.id)
    telegram_message = await telethon_client.get_messages(entity, ids=message.message_id)

    if not telegram_message:
        raise RuntimeError("Tidak menemukan media pada pesan tersebut.")

    result = await telethon_client.download_media(telegram_message, file=str(target_path))
    if not result:
        raise RuntimeError("Download media melalui Telethon gagal.")


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


async def _deliver_transcription(message: Message, result: TranscriptionResult) -> None:
    plain_text = result.to_plain_text()
    if not plain_text:
        await message.answer("Transkrip kosong diterima dari Groq.")
        return

    if len(plain_text) <= TELEGRAM_MESSAGE_LIMIT:
        await message.answer(plain_text)
    else:
        preview = plain_text[:TELEGRAM_MESSAGE_LIMIT]
        await message.answer(
            preview + "\n\n[Transkrip dipotong. Versi lengkap tersedia di lampiran.]"
        )

    await _send_transcript_files(message, result, plain_text)


async def _send_transcript_files(
    message: Message,
    result: TranscriptionResult,
    plain_text: str,
) -> None:
    txt_buffer = io.BytesIO(plain_text.encode("utf-8"))
    txt_file = BufferedInputFile(
        txt_buffer.getvalue(),
        filename="transcript.txt",
    )
    await message.answer_document(
        document=txt_file,
        caption="Transkrip teks tanpa timestamp.",
    )

    if result.segments:
        try:
            srt_content = result.to_srt()
        except ValueError:
            logger.info("SRT output tidak tersedia karena segment informasi tidak lengkap.")
            return

        if srt_content:
            srt_buffer = io.BytesIO(srt_content.encode("utf-8"))
            srt_file = BufferedInputFile(
                srt_buffer.getvalue(),
                filename="transcript.srt",
            )
            await message.answer_document(
                document=srt_file,
                caption="Transkrip format SRT.",
            )
