import logging
import logging.config
import os
from pathlib import Path

import yaml


# def setup_logging(config: LoggingConfig) -> None:
#     if os.path.exists(config.config_path) and config:
#         with open(config.config_path, "r") as f:
#             logging_config = yaml.safe_load(f)
#         logging.config.dictConfig(logging_config)
    
#     else:
#         logging.basicConfig(level=logging.DEBUG)


def setup_logging(path: str | Path) -> None:
    if os.path.exists(path):
        with open(path, "r") as f:
            logging_config = yaml.safe_load(f)
        logging.config.dictConfig(logging_config)
    
    else:
        logging.basicConfig(level=logging.DEBUG)
