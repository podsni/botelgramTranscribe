from __future__ import annotations

import asyncio
import io
import logging
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiogram import Router
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.chat_action import ChatActionSender
from requests import HTTPError
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TransferSpeedColumn,
)

from ..services import (
    ProviderPreferences,
    TranscriberRegistry,
    TelethonDownloadService,
    TranscriptionResult,
)

logger = logging.getLogger(__name__)

router = Router()

TELEGRAM_FILE_DOWNLOAD_LIMIT = 2 * 1024 * 1024 * 1024  # 2 GB via MTProto.
TELEGRAM_MESSAGE_LIMIT = 4000
AUDIO_CONVERSION_THRESHOLD = 15 * 1024 * 1024  # Convert to mp3 when file size >= 15MB.
PROGRESS_BAR_THRESHOLD = 50 * 1024 * 1024  # Show progress bar for downloads >= 50MB.
DEFAULT_PAYLOAD_LIMIT = 25 * 1024 * 1024  # Fallback payload limit (~25MB).


@dataclass
class MediaMeta:
    display_name: str
    suffix: str
    file_size: Optional[int]


@router.message()
async def handle_media(
    message: Message,
    telethon_downloader: TelethonDownloadService,
    transcriber_registry: TranscriberRegistry,
    provider_preferences: ProviderPreferences,
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

    download_path = _build_download_path(meta)
    cleanup_paths = {download_path}
    prepared_path: Path = download_path

    requested_provider = provider_preferences.get(message.chat.id)
    transcriber = transcriber_registry.get(requested_provider)
    if not transcriber:
        fallback = transcriber_registry.default_provider
        transcriber = transcriber_registry.get(fallback)
        provider_preferences.set(message.chat.id, fallback)
        requested_provider = fallback

    if not transcriber:
        await message.answer("Tidak ada provider transkripsi yang tersedia saat ini.")
        return

    provider_name = getattr(transcriber, "provider_name", requested_provider)
    payload_limit = getattr(transcriber, "max_payload_bytes", DEFAULT_PAYLOAD_LIMIT)

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            logger.info(
                "Starting download for %s (%s bytes) in chat %s",
                meta.display_name,
                meta.file_size,
                message.chat.id,
            )
            await _download_media(telethon_downloader, message, download_path, meta)
            logger.info(
                "Download complete: %s (%s bytes)",
                download_path,
                download_path.stat().st_size if download_path.exists() else "unknown",
            )

            prepared_path = await asyncio.to_thread(
                _prepare_audio_for_transcription,
                download_path,
                meta.file_size,
            )
            cleanup_paths.add(prepared_path)

            try:
                payload_size = prepared_path.stat().st_size
            except OSError:
                payload_size = None

            if payload_limit and payload_size and payload_size > payload_limit:
                logger.warning(
                    "Prepared audio %s is %s bytes, exceeds payload limit for provider %s.",
                    prepared_path,
                    payload_size,
                    provider_name,
                )
                limit_mb = payload_limit / (1024 * 1024)
                await message.answer(
                    "File sudah dikonversi, tetapi masih terlalu besar untuk "
                    f"provider {provider_name} (maks sekitar {limit_mb:.1f}MB). "
                    "Silakan kompres lagi atau kirim bagian yang lebih pendek."
                )
                return

            logger.info("Starting transcription via %s for %s", provider_name, prepared_path)
            result = await asyncio.to_thread(transcriber.transcribe, prepared_path)
            await _deliver_transcription(message, result)
        except HTTPError as http_err:
            logger.exception("%s API error during transcription", provider_name.capitalize())
            status_code = http_err.response.status_code if http_err.response is not None else None
            if status_code == 413:
                await message.answer(
                    f"{provider_name.capitalize()} menolak file karena terlalu besar (HTTP 413). "
                    "Silakan kompres ulang sebelum mencoba lagi."
                )
            else:
                await message.answer(
                    f"{provider_name.capitalize()} API mengembalikan kesalahan: "
                    f"{status_code or http_err}"
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
                    logger.warning("Gagal menghapus file sementara %s", path, exc_info=True)


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


def _build_download_path(meta: MediaMeta) -> Path:
    downloads_dir = Path.home() / "Downloads" / "transhades"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    sanitized = _sanitize_filename(meta.display_name)
    suffix = meta.suffix or ".bin"
    filename = sanitized if sanitized.endswith(suffix) else f"{sanitized}{suffix}"
    return downloads_dir / f"{timestamp}_{filename}"


def _sanitize_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name or "media")
    return cleaned.strip("_") or "media"


async def _download_media(
    downloader: TelethonDownloadService,
    message: Message,
    target_path: Path,
    meta: MediaMeta,
) -> None:
    progress: Progress | None = None
    task_id: int | None = None

    def progress_callback(current: int, total: int) -> None:
        if progress and task_id is not None:
            progress.update(task_id, completed=current, total=total or meta.file_size or 0)

    if (meta.file_size or 0) >= PROGRESS_BAR_THRESHOLD:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeElapsedColumn(),
            transient=True,
        )
        progress.start()
        total_size = meta.file_size if (meta.file_size and meta.file_size > 0) else None
        task_id = progress.add_task(
            description=f"Mendownload {meta.display_name}",
            total=total_size,
        )
        logger.info("Progress bar diaktifkan untuk unduhan besar.")

    try:
        await downloader.download_media(
            chat_id=message.chat.id,
            message_id=message.message_id,
            file_path=str(target_path),
            progress_callback=progress_callback if progress else None,
        )
    finally:
        if progress:
            progress.stop()


def _prepare_audio_for_transcription(source_path: Path, file_size: Optional[int]) -> Path:
    if not source_path.exists():
        logger.warning("Source path %s tidak ditemukan.", source_path)
        return source_path

    actual_size = file_size or source_path.stat().st_size
    suffix = source_path.suffix.lower()

    if suffix == ".mp3" and actual_size < AUDIO_CONVERSION_THRESHOLD:
        logger.info(
            "Skipping compression for %s (size %s bytes below threshold).",
            source_path,
            actual_size,
        )
        return source_path

    target_path: Path
    command: list[str]

    if suffix == ".mp3":
        target_path = source_path.with_name(f"{source_path.stem}_compressed.mp3")
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "112k",
            str(target_path),
        ]
    else:
        target_path = source_path.with_suffix(".mp3")
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "96k",
            str(target_path),
        ]

    logger.info(
        "Converting %s (%s bytes) to %s at %s",
        source_path,
        actual_size,
        target_path.suffix,
        target_path,
    )

    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.stderr:
            logger.debug("ffmpeg stderr: %s", result.stderr.decode("utf-8", errors="ignore"))
        try:
            new_size = target_path.stat().st_size
        except OSError:
            new_size = "unknown"
        logger.info("Conversion complete for %s (%s bytes).", target_path, new_size)
        return target_path
    except subprocess.CalledProcessError as err:
        logger.error(
            "ffmpeg conversion failed for %s: %s",
            source_path,
            err.stderr.decode("utf-8", errors="ignore"),
        )
        return source_path


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
