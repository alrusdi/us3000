from .settings import *

DEBUG = True
TEST_CLIENTSIDE_CODE = False

LOGGING['loggers'].update({
    'general': {
        'handlers': ['general_log',],
        'level': 'INFO',
        'propagate': True,
    }
})