from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..services import ProviderPreferences, TranscriberRegistry

router = Router()


@router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        "Kirim atau forward file audio, voice note, atau video ke bot ini. "
        "Bot akan mengunduh hingga 2GB dan mengirimkan transkrip dari provider pilihan Anda "
        "(Groq atau Deepgram). Gunakan /provider untuk mengganti layanan."
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Gunakan bot ini dengan mengirimkan atau mem-forward media audio/video. "
        "Bot akan mengonversi file besar ke mp3 bila diperlukan dan mengirimkan hasil "
        "transkrip sebagai teks, file .txt, dan .srt. "
        "Gunakan /provider <groq|deepgram> untuk memilih penyedia transkripsi per chat."
    )


def _build_provider_keyboard(transcriber_registry: TranscriberRegistry, current: str) -> InlineKeyboardMarkup:
    buttons = []
    for provider in transcriber_registry.providers():
        label = "✅ " + provider if provider == current else provider
        buttons.append(
            [InlineKeyboardButton(text=label.title(), callback_data=f"provider:{provider}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("provider"))
async def provider_command(
    message: Message,
    transcriber_registry: TranscriberRegistry,
    provider_preferences: ProviderPreferences,
) -> None:
    current = provider_preferences.get(message.chat.id)
    keyboard = _build_provider_keyboard(transcriber_registry, current)
    await message.answer(
        "Pilih penyedia transkripsi yang ingin digunakan untuk chat ini:",
        reply_markup=keyboard,
    )


@router.callback_query(lambda c: c.data and c.data.startswith("provider:"))
async def provider_callback(
    query: CallbackQuery,
    transcriber_registry: TranscriberRegistry,
    provider_preferences: ProviderPreferences,
) -> None:
    if not query.data:
        return

    provider = query.data.split(":", maxsplit=1)[1]
    if provider not in transcriber_registry.providers():
        await query.answer("Provider tidak tersedia.", show_alert=True)
        return

    provider_preferences.set(query.message.chat.id, provider)
    keyboard = _build_provider_keyboard(transcriber_registry, provider)
    await query.message.edit_text(
        f"Provider transkripsi diubah ke {provider}.",
        reply_markup=keyboard,
    )
    await query.answer("Provider diperbarui.")
