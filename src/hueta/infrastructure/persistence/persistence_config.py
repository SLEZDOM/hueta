from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol


@dataclass(frozen=True)
class BaseDBConfig(Protocol):

    @abstractmethod
    def url(self) -> str:
        pass


@dataclass(frozen=True)
class MySQLConfig(BaseDBConfig):
    connector: str
    host: str
    port: int
    login: str
    password: str
    name: str
    echo: bool = False

    def url(self) -> str:
        return f"mysql+{self.connector}://{self.login}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass(frozen=True)
class PostgresConfig(BaseDBConfig):
    connector: str
    host: str
    port: int
    login: str
    password: str
    name: str
    echo: bool = False

    def url(self) -> str:
        return f"postgresql+{self.connector}://{self.login}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass(frozen=True)
class SQLiteConfig(BaseDBConfig):
    connector: str
    path: str
    echo: bool = False

    def url(self) -> str:
        return f"sqlite+{self.connector}:///{self.path}"


@dataclass(frozen=True)
class RedisConfig(BaseDBConfig):
    host: str
    port: int
    db: int

    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class StorageType(str, Enum):
    MEMORY = "memory"
    REDIS = "redis"


@dataclass(frozen=True)
class BaseStorageConfig(Protocol):
    type: StorageType
    config: Optional[BaseDBConfig] = None


@dataclass(frozen=True)
class MemoryStorageConfig(BaseStorageConfig):
    type: StorageType = StorageType.MEMORY


@dataclass(frozen=True)
class DBStorageConfig(BaseStorageConfig):
    type: StorageType
    config: BaseDBConfig
