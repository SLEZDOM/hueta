from dataclasses import dataclass
import os
from pathlib import Path

import yaml

from hueta_bot.infrastructure.persistence.persistence_config import (
    BaseDBConfig,
    BaseStorageConfig,
    SQLiteConfig,
    PostgresConfig,
    MySQLConfig,
    RedisConfig,
    StorageType,
    MemoryStorageConfig,
    DBStorageConfig
)


class ConfigParseError(ValueError):
    pass


def get_env_var(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ConfigParseError(f"Environment variable {key} is not set.")
    return value


def load_yaml_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_db_config(db_config: dict) -> BaseDBConfig:
    db_type: str = db_config["type"]

    if db_type.startswith("sqlite"):
        return SQLiteConfig(
            connector=db_config.get("connector", "sqlite"),
            path=get_env_var("BOT_DATABASE_SQLITE_PATH")
        )

    elif db_type.startswith("mysql"):
        return MySQLConfig(
            connector=db_config.get("connector", "pymysql"),
            host=get_env_var("BOT_DATABASE_HOST"),
            port=int(get_env_var("BOT_DATABASE_PORT")),
            login=get_env_var("BOT_DATABASE_LOGIN"),
            password=get_env_var("BOT_DATABASE_PASSWORD"),
            name=get_env_var("BOT_DATABASE_NAME"),
        )

    elif db_type.startswith("postgres"):
        return PostgresConfig(
            connector=db_config.get("connector", "asyncpg"),
            host=get_env_var("BOT_DATABASE_HOST"),
            port=int(get_env_var("BOT_DATABASE_PORT")),
            login=get_env_var("BOT_DATABASE_LOGIN"),
            password=get_env_var("BOT_DATABASE_PASSWORD"),
            name=get_env_var("BOT_DATABASE_NAME"),
        )

    else:
        raise ConfigParseError(f"Unsupported database type: {db_type}")


def get_storage_config(storage_config: dict) -> BaseStorageConfig:
    storage_type = StorageType(storage_config["type"])

    if storage_type == StorageType.MEMORY:
        return MemoryStorageConfig()

    elif storage_type == StorageType.REDIS:
        return DBStorageConfig(
            config=RedisConfig(
                host=get_env_var("BOT_STORAGE_REDIS_HOST"),
                port=int(get_env_var("BOT_STORAGE_REDIS_PORT")),
                db=int(get_env_var("BOT_STORAGE_REDIS_DB")),
            ),
            type=StorageType.REDIS
        )

    else:
        raise ConfigParseError(f"Unsupported storage type: {storage_type}")


@dataclass
class BotConfig:
    bot_token: str
    storage: BaseStorageConfig
    db: BaseDBConfig
    logging_config_path: str


def load_bot_config() -> BotConfig:
    config_path: Path = get_env_var("BOT_CONFIG_PATH")
    logging_config_path: Path = get_env_var("LOGGING_CONFIG_PATH")

    config_data: dict = load_yaml_config(config_path)

    return BotConfig(
        bot_token=get_env_var("BOT_TOKEN"),
        storage=get_storage_config(config_data["storage"]),
        db=get_db_config(config_data["db"]),
        logging_config_path=logging_config_path
    )
