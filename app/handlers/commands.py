from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        "Kirim atau forward file audio, voice note, atau video ke bot ini. "
        "Bot akan mengunduh hingga 2GB dan mengirimkan transkrip dari Groq Whisper."
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Gunakan bot ini dengan mengirimkan atau mem-forward media audio/video. "
        "Bot akan mengonversi file besar ke mp3 bila diperlukan dan mengirimkan hasil "
        "transkrip sebagai teks, file .txt, dan .srt."
    )
