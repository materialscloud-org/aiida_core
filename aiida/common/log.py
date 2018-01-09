# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
import logging
from copy import deepcopy
from logging import config
from aiida.common import setup

# Custom logging level, intended specifically for informative log messages
# reported during WorkChains and Workflows. We want the level between INFO(20)
# and WARNING(30) such that it will be logged for the default loglevel, however
# the value 25 is already reserved for SUBWARNING by the multiprocessing module.
LOG_LEVEL_REPORT = 23
logging.addLevelName(LOG_LEVEL_REPORT, 'REPORT')

# The AiiDA logger
aiidalogger = logging.getLogger('aiida')

# A logging filter that can be used to disable logging
class NotInTestingFilter(logging.Filter):

    def filter(self, record):
        from aiida import settings
        return not settings.TESTING_MODE

# The default logging dictionary for AiiDA that can be used in conjunction
# with the config.dictConfig method of python's logging module
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s',
        },
        'halfverbose': {
            'format': '%(asctime)s, %(name)s: [%(levelname)s] %(message)s',
            'datefmt': '%m/%d/%Y %I:%M:%S %p',
        },
    },
    'filters': {
        'testing': {
            '()': NotInTestingFilter
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'halfverbose',
            'filters': ['testing']
        },
        'daemon_logfile': {
            'level': 'DEBUG',
            'formatter': 'halfverbose',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': setup.DAEMON_LOG_FILE,
            'encoding': 'utf8',
            'maxBytes': 100000,
        },
        'dblogger': {
            # setup.get_property takes the property from the config json file
            # The key used in the json, and the default value, are
            # specified in the _property_table inside aiida.common.setup
            # NOTE: To modify properties, use the 'verdi devel setproperty'
            #   command and similar ones (getproperty, describeproperties, ...)
            'level': setup.get_property('logging.db_loglevel'),
            'class': 'aiida.utils.logger.DBLogHandler',
        },
    },
    'loggers': {
        'aiida': {
            'handlers': ['console', 'dblogger'],
            'level': setup.get_property('logging.aiida_loglevel'),
            'propagate': False,
        },
        'paramiko': {
            'handlers': ['console'],
            'level': setup.get_property('logging.paramiko_loglevel'),
            'propagate': False,
        },
        'alembic': {
            'handlers': ['console'],
            'level': setup.get_property('logging.alembic_loglevel'),
            'propagate': False,
        },
        'sqlalchemy': {
            'handlers': ['console'],
            'level': setup.get_property('logging.sqlalchemy_loglevel'),
            'propagate': False,
            'qualname': 'sqlalchemy.engine',
        },
    },
}

def configure_logging(daemon=False, daemon_handler='daemon_logfile'):
    """
    Setup the logging by retrieving the LOGGING dictionary from aiida and passing it to
    the python module logging.config.dictConfig. If the logging needs to be setup for the
    daemon running a task for one of the celery workers, set the argument 'daemon' to True.
    This will cause the 'daemon_handler' to be added to all the configured loggers. This
    handler needs to be defined in the LOGGING dictionary and is 'daemon_logfile' by
    default. If this changes in the dictionary, be sure to pass the correct handle name.
    The daemon handler should be a RotatingFileHandler that writes to the daemon log file.

    :param daemon: configure the logging for a daemon task by adding a file handler instead
        of the default 'console' StreamHandler
    :param daemon_handler: name of the file handler in the LOGGING dictionary
    """
    config = deepcopy(LOGGING)

    # Add the daemon file handler to all loggers if daemon=True
    if daemon is True:
        for name, logger in config.get('loggers', {}).iteritems():
            logger.setdefault('handlers', []).append(daemon_handler)

    logging.config.dictConfig(config)