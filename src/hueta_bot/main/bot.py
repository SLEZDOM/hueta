import asyncio

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.base import BaseStorage, BaseEventIsolation
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import (
    RedisStorage,
    DefaultKeyBuilder,
    RedisEventIsolation
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka

from hueta_bot.presentation.middlewares import setup_middlewares
from hueta_bot.presentation.handlers import setup_handlers
from hueta_bot.infrastructure.logging import setup_logging
from hueta_bot.main.di import setup_bot_container
from hueta_bot.main.config import (
    load_bot_config,
    BotConfig,
    BaseStorageConfig,
    StorageType
)


def create_storage(storage_config: BaseStorageConfig) -> BaseStorage:
    if storage_config.type == StorageType.MEMORY:
        return MemoryStorage()

    elif storage_config.type == StorageType.REDIS:
        if storage_config.config is None:
            raise ValueError("you have to specify redis config for use redis storage")

        return RedisStorage.from_url(
            storage_config.config.url(),
            key_builder=DefaultKeyBuilder(
                with_bot_id=True,
                with_destiny=True
            )
        )

    else:
        raise NotImplementedError


def create_event_isolation(
    storage_config: BaseStorageConfig
) -> BaseEventIsolation:
    if storage_config.type == StorageType.MEMORY:
        return SimpleEventIsolation()

    elif storage_config.type == StorageType.REDIS:
        if storage_config.config is None:
            raise ValueError("you have to specify redis config for use redis storage")

        return RedisEventIsolation.from_url(storage_config.config.url())

    else:
        raise NotImplementedError


def create_bot(bot_config: BotConfig) -> Bot:
    bot = Bot(
        token=bot_config.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    return bot


def create_dispatcher(
    bot_config: BotConfig
) -> Dispatcher:
    storage: BaseStorage = create_storage(
        storage_config=bot_config.storage
    )
    event_isolation: BaseEventIsolation = create_event_isolation(
        storage_config=bot_config.storage
    )

    dispatcher = Dispatcher(
        storage=storage,
        events_isolation=event_isolation
    )

    return dispatcher


async def main() -> None:
    bot_config: BotConfig = load_bot_config()

    setup_logging(bot_config.logging_config_path)

    bot = create_bot(bot_config=bot_config)
    dispatcher = create_dispatcher(bot_config=bot_config)

    bot_container = setup_bot_container()

    setup_middlewares(
        bot=bot,
        dispatcher=dispatcher
    )
    setup_handlers(
        dispatcher=dispatcher
    )

    setup_dishka(
        container=bot_container,
        router=dispatcher,
        auto_inject=True
    )

    await dispatcher.start_polling(bot)


asyncio.run(main())
