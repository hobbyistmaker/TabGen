import logging


class Configuration:

    LOG_FILE = 'tabgen.log'
    LOG_LEVEL = logging.DEBUG

    # Select default command settings
    DEFAULT_TAB_WIDTH = 8
    DEFAULT_MATERIAL_THICKNESS = 3.2
    DEFAULT_START_WITH_TAB = True
    DEFAULT_MAKE_PARAMETRIC = False

    # Select one of the two following
    DEFAULT_USER_WIDTH_TAB = True
    DEFAULT_AUTO_WIDTH_TAB = False

    # Select one of the two following
    DEFAULT_SINGLE_EDGE = False
    DEFAULT_DUAL_EDGE = True
