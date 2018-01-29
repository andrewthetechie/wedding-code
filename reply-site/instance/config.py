import sys
import logging
from decouple import config


class Config(object):
    """Configurations for Production."""
    DEBUG = config("DEBUG_MODE", cast=bool, default=False)
    TESTING = config("TESTING_MODE", cast=bool, default=False)
    PRODUCTION = config("TESTING_MODE", cast=bool, default=False)
    CSRF_ENABLED = True
    SECRET = config('FLASK_SECRET', cast=str)
    SQLALCHEMY_TRACK_MODIFICATIONS = config('SQLALCHEMY_TRACK_MODIFICATIONS', cast=bool, default=False)
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URI')
    # Twilio config
    TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', cast=str)

    _log_level = config('LOG_LEVEL', default='error', cast=str).lower()

    LOG_LEVEL = logging.ERROR

    # Logging config
    if _log_level == 'critical':
        LOG_LEVEL = logging.CRITICAL
    if _log_level == 'warning':
        LOG_LEVEL = logging.warning
    if _log_level == 'info':
        LOG_LEVEL = logging.INFO
    if _log_level == 'debug':
        LOG_LEVEL = logging.DEBUG

    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s - %(levelname)s %(module)s '
                          'P%(process)d T%(thread)d %(message)s'
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'verbose',
            }
        },
        'loggers': {
            'reply_site': {
                'handlers': ['stdout'],
                'level': LOG_LEVEL,
                'propagate': True,
            },
        }
    }



