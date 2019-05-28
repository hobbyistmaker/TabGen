# Author-
# Description-
import logging
import sys

from collections import namedtuple

import adsk.cam
import adsk.core
import adsk.fusion
import traceback

from adsk.core import Application

from .config import Configuration
from .core import definitions as defs
from .core.handlers import CommandCreatedEventHandlerPanel

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

Command = namedtuple('Command', ['cid', 'name', 'description'])

class CommandCreationException(Exception): pass

class CommandDefinitionFailureException(Exception): pass

class ButtonDefinitionFailureException(Exception): pass


def initialize_panel(ui, command):
    cmd_def = ui.commandDefinitions.itemById(command.cid)
    return cmd_def if cmd_def else create_command(ui, command)


def create_command(ui, command):
    try:
        return ui.commandDefinitions.addButtonDefinition(
            command.cid,
            command.name,
            command.description
        )
    except:
        raise ButtonDefinitionFailureException


def add_command(panel, cmd_def):
    try:
        control = panel.controls.itemById(cmd_def.id)
        return control if control else panel.controls.addCommand(cmd_def)
    except:
        raise CommandDefinitionFailureException


command = Command(defs.tabGenCommandId, 'Generate Tabs',
                  'Creates finger-joint tabs and gaps on rectangular faces')


def run(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create the command definition and add a button to the Add-ins panel
        # per Autodesk UI guidance.
        addins = ui.allToolbarPanels.itemById(defs.parentPanelId)
        cmd_def = initialize_panel(ui, command)
        control = add_command(addins, cmd_def)

        panel = CommandCreatedEventHandlerPanel(app, ui, Configuration)
        handlers.append(panel)

        if not cmd_def.commandCreated.add(panel):
            raise CommandCreationException

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

        addins = ui.allToolbarPanels.itemById(defs.parentPanelId)
        cmd_def = initialize_panel(ui, command)
        control = addins.controls.itemById(cmd_def.id)

        if control:
            control.deleteMe()
        if cmd_def:
            cmd_def.deleteMe()
    except:
        msg = 'TabGen add-in stop failed: {}'.format(traceback.format_exc())
        logger.debug(msg)
        if ui:
            ui.messageBox(msg)
