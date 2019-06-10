# Author-
# Description-
import logging

import adsk.cam
import adsk.core
import adsk.fusion
import traceback

from .config import Configuration
from .core import definitions as defs
from .core.handlers import CommandCreatedEventHandlerPanel
from .core.handlers import SketchPanel

START_MSG = """The "Generate Tabs" command has been added
to the Add-ins panel of the MODEL workspace."""

# The following two lines must be uncommented
# for logging to work correctly while running
# within Fusion 360
# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)
logging.basicConfig(filename=Configuration.LOG_FILE,
                    level=Configuration.LOG_LEVEL)
logger = logging.getLogger('tabgen')

handlers = []


class CommandCreationError(Exception): pass


class CommandDefinitionFailure(Exception): pass


class ButtonDefinitionFailure(Exception): pass


def initialize_panel(ui):
    cmd_def = ui.commandDefinitions.itemById(defs.tabGenCommandId)
    return cmd_def if cmd_def else create_command(ui)


def create_command(ui):
    try:
        return ui.commandDefinitions.addButtonDefinition(
            defs.tabGenCommandId,
            'Generate Tabs',
            'Creates finger-joint tabs and gaps on rectangular faces'
        )
    except:
        raise ButtonDefinitionFailure


def add_command(config):
    addins = config.ui.allToolbarPanels.itemById(defs.parentPanelId)
    cmd_def = initialize_panel(config.ui)

    existing_control = addins.controls.itemById(cmd_def.id)
    if not existing_control:
        addins.controls.addCommand(cmd_def)

    panel = CommandCreatedEventHandlerPanel(config)

    if not cmd_def.commandCreated.add(panel):
        raise CommandCreationError

    return panel


def add_sketch_command(app, ui):
    addins = ui.allToolbarPanels.itemById(defs.parentPanelId)
    cmd_def = ui.commandDefinitions.itemById('sketchTestPanel')
    if not cmd_def:
        cmd_def = ui.commandDefinitions.addButtonDefinition('sketchTestPanel', 'Test Sketch Routine',
                                                            'Tests the TabGen sketch routine.')

    existing_control = addins.controls.itemById(cmd_def.id)
    if not existing_control:
        addins.controls.addCommand(cmd_def)

    panel = SketchPanel(app, ui)

    if not cmd_def.commandCreated.add(panel):
        raise CommandCreationError

    return panel


def run(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        delete_tabgen(ui)

        # Create the command definition and add a button to the Add-ins panel
        # per Autodesk UI guidance.
        panel = add_command(Configuration(app))
        handlers.append(panel)

        # If the command is being manually started let the user know it's done
        if context['IsApplicationStartup'] is False:
            ui.messageBox(START_MSG)

    except:
        msg = 'Failed:\n{}'.format(traceback.format_exc())
        logger.debug(msg)
        if ui:
            ui.messageBox(msg)


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        delete_tabgen(ui)

    except:
        msg = 'TabGen add-in stop failed: {}'.format(traceback.format_exc())
        logger.debug(msg)
        if ui:
            ui.messageBox(msg)


def delete_tabgen(ui):
    addins = ui.allToolbarPanels.itemById(defs.parentPanelId)
    cmd_def = initialize_panel(ui)
    control = addins.controls.itemById(cmd_def.id)
    if control:
        control.deleteMe()
    if cmd_def:
        cmd_def.deleteMe()


def delete_sketchtest(ui):
    addins = ui.allToolbarPanels.itemById(defs.parentPanelId)
    cmd_def = ui.commandDefinitions.itemById('sketchTestPanel')
    control = addins.controls.itemById(cmd_def.id)
    if control:
        control.deleteMe()
    if cmd_def:
        cmd_def.deleteMe()
