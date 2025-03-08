from typing import AsyncGenerator, AsyncIterable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    make_async_container,
    provide,
)

from application.ports.persistence.transaction_manager import (
    TransactionManager
)
from infrastructure.persistence.transaction_manager import (
    SQLAlchemyTransactionManager
)
from bot_config import (
    load_bot_config,
    BotConfig,
    BaseDBConfig,
)


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_config(
        self,
    ) -> BotConfig:
        config = load_bot_config()
        return config

    @provide(scope=Scope.APP)
    def provide_db_config(
        self,
        config: BotConfig
    ) -> BaseDBConfig:
        return config.db


class PersistenceProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_engine(
        self,
        db_config: BaseDBConfig
    ) -> AsyncGenerator[AsyncEngine, None]:
        engine: AsyncEngine = create_async_engine(
            db_config.url(),
            future=True,
        )

        yield engine

        await engine.dispose()

    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self,
        engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    transaction_manager_provider = provide(
        SQLAlchemyTransactionManager,
        scope=Scope.REQUEST,
        provides=TransactionManager,
    )


def setup_bot_providers() -> list[Provider]:
    providers = [
        ConfigProvider(),
        PersistenceProvider(),
    ]

    return providers


def setup_bot_container() -> AsyncContainer:
    bot_providers = setup_bot_providers()

    bot_container = make_async_container(*bot_providers)

    return bot_container
