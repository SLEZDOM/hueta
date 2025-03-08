from aiogram import Dispatcher

from .main import setup


def setup_handlers(
    dispatcher: Dispatcher
) -> None:
    setup(dispatcher=dispatcher)
