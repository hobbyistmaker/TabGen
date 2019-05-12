# Author-
# Description-
import logging

import adsk.cam
import adsk.core
import adsk.fusion
import traceback

from .config import Configuration
from .handlers import handlers
from .handlers import CommandCreatedEventHandlerPanel
from .util import tabGenCommandId

point3d = adsk.core.Point3D

# The following two lines must be uncommented
# for logging to work correctly while running
# within Fusion 360
# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)
logging.basicConfig(filename=Configuration.LOG_FILE,
                    level=Configuration.LOG_LEVEL)
logger = logging.getLogger('tabgen')


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        logger.debug('Creating CommandEventHandlerPanel definition.')
        # Create the command definition and add a button to the Add-ins panel
        # per Autodesk UI guidance.
        cmdDef = ui.commandDefinitions.addButtonDefinition(
            tabGenCommandId,
            'Generate Tabs',
            'Creates finger-joint tabs and gaps on rectangular faces')
        createPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        createPanel.controls.addCommand(cmdDef)

        # Set up the command created event handler
        onCommandCreated = CommandCreatedEventHandlerPanel()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        # If the command is being manually started let the user know it's done
        # if context['IsApplicationStartup'] is False:
        #     ui.messageBox('The "Generate Tabs" command has been added\nto the MODIFY panel of the MODEL workspace.')

    except:
        msg = 'Failed:\n{}'.format(traceback.format_exc())
        logger.debug(msg)
        if ui:
            ui.messageBox(msg)
        stop(context)


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        modifyPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        tabGenButton = modifyPanel.controls.itemById(tabGenCommandId)
        if tabGenButton:
            tabGenButton.deleteMe()

        cmdDef = ui.commandDefinitions.itemById(tabGenCommandId)
        if cmdDef:
            cmdDef.deleteMe()
        logger.debug('TabGen add-in stopped.')

    except:
        msg = 'TabGen add-in stop failed: {}'.format(traceback.format_exc())
        logger.debug(msg)
        if ui:
            ui.messageBox(msg)
