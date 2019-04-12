import adsk.core
import traceback

from ..tabgen import createfingers
from ..util import uimessage
from ..util import mtlThickInputId
from ..util import (fingerTypeId,
                    selectedFaceInputId,
                    startWithTabInputId,
                    tabWidthInputId)

# Constants
executionFailedMsg = 'TabGen executon failed: {}'


class CommandExecuteHandler(adsk.core.CommandEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui

    def notify(self, args):
        try:
            command = args.firingEvent.sender
            commandInputs = command.commandInputs
            selInput = commandInputs.itemById(selectedFaceInputId)

            faces = [selInput.selection(j).entity
                     for j in range(selInput.selectionCount)]


            finger_type = commandInputs.itemById(fingerTypeId).selectedItem.name
            tab_width = commandInputs.itemById(tabWidthInputId).value
            material_thickness = commandInputs.itemById(mtlThickInputId).value
            start_tab = commandInputs.itemById(startWithTabInputId).value

            createfingers.create_fingers(finger_type,
                                         tab_width,
                                         material_thickness,
                                         start_tab,
                                         faces,
                                         self.app,
                                         self.ui)

        except:
            uimessage(self.ui, executionFailedMsg, traceback.format_exc())
