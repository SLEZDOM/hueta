from dataclasses import dataclass


@dataclass(frozen=True)
class LoggingConfig:
    config_path: str
    default_log_file: str = "logs/app.log"
