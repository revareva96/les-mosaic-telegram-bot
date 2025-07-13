import logging
from logging.config import dictConfig

from bootstrap.settings import AppSettings


def setup_logger(config: AppSettings):
    logging_level = logging.getLevelName(config.log_level)

    dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                },
            },
            'handlers': {
                'default': {
                    'level': logging_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                },
            },
            'loggers': {
                'les_mosaic': {
                    'handlers': ['default'],
                    'level': logging_level,
                    'propagate': True,
                },
                'httpx': {
                    'handlers': ['default'],
                    'level': 'ERROR',
                    'propagate': False,
                },
            },
        }
    )
