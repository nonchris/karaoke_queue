import os
import logging
from collections import deque


# copied from:
# https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/35804945#35804945
def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).data('that worked')
    >>> logging.data('so did this')
    >>> logging.DATA
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

# path for databases or config files
if not os.path.exists('data/'):
    os.mkdir('data/')

addLoggingLevel("DATA", 5)

# set logging format
formatter = logging.Formatter("[{asctime}] [{levelname}] [{threadName}][{module}.{funcName}] {message}", style="{")
rich_formatter = logging.Formatter("[{asctime}] [{levelname}] [{threadName}] {message}",
                                   style="{", datefmt="%d.%m %H:%M:%S")

# logger for writing to file
file_logger = logging.FileHandler('data/events.log')
file_logger.setLevel(logging.INFO)
file_logger.setFormatter(formatter)

# logger for console prints
console_logger = logging.StreamHandler()
console_logger.setLevel(logging.DEBUG)
console_logger.setFormatter(formatter)


# get new logger
logger = logging.getLogger('logger')
# set logger to lowest level we wanna log anywhere!
# if we don't do this logging will assume WARNING as default
# handlers won't get messages for lower levels, because they're discarded
# why the fuck is this how it's done?! - serious. what a crap...
logger.setLevel(logging.DATA)

# register loggers
# logger.setLevel(logging.INFO)
logger.addHandler(file_logger)
logger.addHandler(console_logger)
