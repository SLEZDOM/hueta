from aiogram import Dispatcher

from . import main


def setup_handlers(
    dispatcher: Dispatcher
) -> None:
    main.setup(
        dispatcher=dispatcher
    )
