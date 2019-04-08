# Author-
# Description-

import adsk.cam
import adsk.core
import adsk.fusion
import traceback

from .tabgen import handlers
from .tabgen import CommandCreatedEventHandlerPanel
from .util import tabGenCommandId

point3d = adsk.core.Point3D


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create the command definition and add a button to the MODIFY panel.
        cmdDef = ui.commandDefinitions.addButtonDefinition(
            tabGenCommandId,
            'Generate Tabs',
            'Creates finger-joint tabs and gaps on rectangular faces')
        createPanel = ui.allToolbarPanels.itemById('SolidModifyPanel')
        createPanel.controls.addCommand(cmdDef)

        # Set up the command created event handler
        onCommandCreated = CommandCreatedEventHandlerPanel(app, ui)
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        # If the command is being manually started let the user know it's done
        if context['IsApplicationStartup'] is False:
            ui.messageBox('The "Generate Tabs" command has been added\nto the MODIFY panel of the MODEL workspace.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        modifyPanel = ui.allToolbarPanels.itemById('SolidModifyPanel')
        tabGenButton = modifyPanel.controls.itemById(tabGenCommandId)
        if tabGenButton:
            tabGenButton.deleteMe()

        cmdDef = ui.commandDefinitions.itemById(tabGenCommandId)
        if cmdDef:
            cmdDef.deleteMe()

    except:
        if ui:
            ui.messageBox('TabGen add-in stop failed: {}'.format(traceback.format_exc()))
