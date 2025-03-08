import logging
from typing import Any, List, Optional, Type

from aiogram import Bot
from aiogram.methods import TelegramMethod, GetUpdates
from aiogram.methods.base import Response, TelegramType
from aiogram.client.session.middlewares.base import (
    BaseRequestMiddleware,
    NextRequestMiddlewareType
)
from aiogram.utils.serialization import (
    deserialize_telegram_object_to_python
)


logger = logging.getLogger(__name__)


class BotRequestLoggerMiddleware(BaseRequestMiddleware):
    def __init__(
        self,
        ignore_methods: Optional[List[Type[TelegramMethod[Any]]]] = None
    ):
        self.ignore_methods = ignore_methods if ignore_methods else []

    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        response = await make_request(bot, method)
        if not isinstance(method, GetUpdates):
            logging.info(
                "Make request with method=%r by bot id=%d, response=%r",
                type(method).__name__,
                bot.id,
                deserialize_telegram_object_to_python(response)
            )

        return response
