from aiogram import Bot, Dispatcher

from .telegram_event_logger_middleware import TelegramEventLoggerMiddleware
from .bot_request_logger_middleware import BotRequestLoggerMiddleware


def setup_middlewares(
    bot: Bot,
    dispatcher: Dispatcher,
) -> None:
    bot.session.middleware(BotRequestLoggerMiddleware())
    dispatcher.update.middleware(TelegramEventLoggerMiddleware())
    dispatcher.errors.middleware(TelegramEventLoggerMiddleware())
