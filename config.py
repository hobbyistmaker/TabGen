import logging


class Configuration:

    # This should be set to wherever the log file
    # should reside. This log file is only used
    # for troubleshooting purposes.
    #
    LOG_FILE = 'tabgen.log'
    # Log Levels use Python logging module settings
    # The only useful options right now are:
    # logging.NOTSET -- no logging will be performed
    # logging.DEBUG -- complete logging will be performed
    #
    # Two additional lines need to be uncommented within
    # the TabGen.py file for logging to work.
    #
    LOG_LEVEL = logging.NOTSET

    # Select default command settings
    DEFAULT_TAB_WIDTH = 8
    DEFAULT_MATERIAL_THICKNESS = 3.2
    DEFAULT_MARGIN_WIDTH = 0
    DEFAULT_START_WITH_TAB = True
    DEFAULT_MAKE_PARAMETRIC = False

    # Select one of the two following
    DEFAULT_USER_WIDTH_TAB = True
    DEFAULT_AUTO_WIDTH_TAB = False

    # Select one of the two following
    DEFAULT_SINGLE_EDGE = False
    DEFAULT_DUAL_EDGE = True

    DEFAULT_WALL_COUNT = 0
