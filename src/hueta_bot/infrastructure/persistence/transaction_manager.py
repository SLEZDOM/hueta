from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from hueta_bot.application.ports.persistence.transaction_manager import (
    TransactionManager
)


class SQLAlchemyTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def commit(self) -> None:
        await self.session.commit()

    async def flush(self, *objects: Any):
        await self.session.flush(objects)

    async def rollback(self) -> None:
        await self.session.rollback()
