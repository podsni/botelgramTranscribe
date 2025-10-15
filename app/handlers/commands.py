from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..services import DeepgramModelPreferences, ProviderPreferences, TranscriberRegistry

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


def _build_provider_keyboard(
    transcriber_registry: TranscriberRegistry,
    provider_preferences: ProviderPreferences,
    deepgram_model_preferences: DeepgramModelPreferences,
    chat_id: int,
) -> InlineKeyboardMarkup:
    current_provider = provider_preferences.get(chat_id)
    keyboard = []
    for provider in transcriber_registry.providers():
        label = provider.title()
        if provider == current_provider:
            label = "✅ " + label
        keyboard.append(
            [InlineKeyboardButton(text=label, callback_data=f"provider:{provider}")]
        )

    if "deepgram" in transcriber_registry.providers():
        current_model = deepgram_model_preferences.get(chat_id)
        model_buttons = []
        for model_code, caption in (("whisper", "Whisper"), ("nova-3", "Nova-3")):
            label = caption
            if current_model == model_code:
                label = "✅ " + caption
            model_buttons.append(
                InlineKeyboardButton(text=label, callback_data=f"deepgram_model:{model_code}")
            )
        keyboard.append(model_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("provider"))
async def provider_command(
    message: Message,
    transcriber_registry: TranscriberRegistry,
    provider_preferences: ProviderPreferences,
    deepgram_model_preferences: DeepgramModelPreferences,
) -> None:
    keyboard = _build_provider_keyboard(
        transcriber_registry,
        provider_preferences,
        deepgram_model_preferences,
        message.chat.id,
    )
    await message.answer(
        "Pilih penyedia transkripsi dan model Deepgram (jika diperlukan) untuk chat ini:",
        reply_markup=keyboard,
    )


@router.callback_query(lambda c: c.data and c.data.startswith("provider:"))
async def provider_callback(
    query: CallbackQuery,
    transcriber_registry: TranscriberRegistry,
    provider_preferences: ProviderPreferences,
    deepgram_model_preferences: DeepgramModelPreferences,
) -> None:
    if not query.data:
        return

    provider = query.data.split(":", maxsplit=1)[1]
    if provider not in transcriber_registry.providers():
        await query.answer("Provider tidak tersedia.", show_alert=True)
        return

    current_provider = provider_preferences.get(query.message.chat.id)
    if provider == current_provider:
        await query.answer("Provider sudah aktif.")
        return

    provider_preferences.set(query.message.chat.id, provider)
    keyboard = _build_provider_keyboard(
        transcriber_registry,
        provider_preferences,
        deepgram_model_preferences,
        query.message.chat.id,
    )
    await query.message.edit_text(
        f"Provider transkripsi diubah ke {provider}.",
        reply_markup=keyboard,
    )
    await query.answer("Provider diperbarui.")


@router.callback_query(lambda c: c.data and c.data.startswith("deepgram_model:"))
async def deepgram_model_callback(
    query: CallbackQuery,
    transcriber_registry: TranscriberRegistry,
    provider_preferences: ProviderPreferences,
    deepgram_model_preferences: DeepgramModelPreferences,
) -> None:
    if not query.data:
        return

    if "deepgram" not in transcriber_registry.providers():
        await query.answer("Deepgram tidak dikonfigurasi.", show_alert=True)
        return

    model = query.data.split(":", maxsplit=1)[1]
    if model not in ("whisper", "nova-3"):
        await query.answer("Model tidak didukung.", show_alert=True)
        return

    current_model = deepgram_model_preferences.get(query.message.chat.id)
    current_provider = provider_preferences.get(query.message.chat.id)

    if model == current_model and current_provider == "deepgram":
        await query.answer("Model Deepgram sudah aktif.")
        return

    deepgram_model_preferences.set(query.message.chat.id, model)
    provider_preferences.set(query.message.chat.id, "deepgram")

    keyboard = _build_provider_keyboard(
        transcriber_registry,
        provider_preferences,
        deepgram_model_preferences,
        query.message.chat.id,
    )
    await query.message.edit_text(
        f"Provider transkripsi diubah ke deepgram dengan model {model}.",
        reply_markup=keyboard,
    )
    await query.answer("Model Deepgram diperbarui.")
