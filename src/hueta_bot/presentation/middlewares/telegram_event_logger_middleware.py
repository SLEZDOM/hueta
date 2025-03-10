import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.utils.serialization import (
    deserialize_telegram_object_to_python
)


logger = logging.getLogger(__name__)


class TelegramEventLoggerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        logging.info(
            "telegram event with event=%r",
            deserialize_telegram_object_to_python(event)
        )

        return await handler(event, data)
