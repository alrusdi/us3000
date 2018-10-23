from .settings import *

DEBUG = True
TEST_CLIENTSIDE_CODE = True

LOGGING['loggers'].update({
    'general': {
        'handlers': ['general_log', ],
        'level': 'INFO',
        'propagate': True,
    }
})