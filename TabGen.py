# Author-
# Description-
import logging

import adsk.cam
import adsk.core
import adsk.fusion
import traceback

from adsk.core import Application

from .config import Configuration
# from .handlers import handlers
# from .handlers import CommandCreatedEventHandlerPanel
from .util import tabGenCommandId
from .core import tabgenerator

point3d = adsk.core.Point3D

# The following two lines must be uncommented
# for logging to work correctly while running
# within Fusion 360
# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)
logging.basicConfig(filename=Configuration.LOG_FILE,
                    level=Configuration.LOG_LEVEL)
logger = logging.getLogger('tabgen')

app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    ui = None
    try:
        tabgenerator.start()

    except:
        msg = 'Failed:\n{}'.format(traceback.format_exc())
        logger.debug(msg)
        if ui:
            ui.messageBox(msg)


def stop(context):
    ui = None
    try:
        tabgenerator.stop()

    except:
        msg = 'TabGen add-in stop failed: {}'.format(traceback.format_exc())
        logger.debug(msg)
        if ui:
            ui.messageBox(msg)
