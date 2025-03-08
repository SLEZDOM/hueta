from aiogram import Dispatcher
from aiogram.types import (
    ErrorEvent,
    Message
)
from aiogram.filters import (
    ExceptionTypeFilter,
    CommandStart
)
from aiogram.exceptions import TelegramNetworkError
from aiogram_dialog.api.exceptions import (
    UnknownIntent,
    OutdatedIntent
)


async def handle_start_command(
    message: Message
):
    ...


async def handle_aiogram_dialog_error(
    error_event: ErrorEvent
):
    # update: Update = error_event.update
    ...


def setup(
    dispatcher: Dispatcher
) -> None:
    dispatcher.errors.register(
        handle_aiogram_dialog_error,
        ExceptionTypeFilter(
            UnknownIntent,
            OutdatedIntent,
        )
    )
    dispatcher.message.register(
        handle_start_command,
        CommandStart()
    )
