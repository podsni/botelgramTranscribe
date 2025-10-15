import logging

from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters

from .config import Settings, load_settings
from .services import GroqTranscriber
from .telegram_handlers import TelegramBotHandlers

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s | %(message)s"


def create_application(settings: Settings) -> Application:
    transcriber = GroqTranscriber(settings.groq_api_key)
    handlers = TelegramBotHandlers(transcriber)

    application = ApplicationBuilder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help_command))
    application.add_handler(
        MessageHandler(
            filters.AUDIO
            | filters.VOICE
            | filters.VIDEO
            | filters.VIDEO_NOTE
            | filters.Document.AUDIO
            | filters.Document.VIDEO,
            handlers.handle_media,
        )
    )
    return application


def run_polling_bot() -> None:
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    settings = load_settings()
    application = create_application(settings)

    logging.getLogger(__name__).info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    run_polling_bot()
