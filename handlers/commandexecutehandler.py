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

            fingerType = commandInputs.itemById(fingerTypeId).selectedItem.name
            tabWidth = commandInputs.itemById(tabWidthInputId).value
            mtlThick = commandInputs.itemById(mtlThickInputId).value
            startWithTab = commandInputs.itemById(startWithTabInputId).value

            uimessage(self.ui, 'tabWidth: {}'.format(tabWidth))

            createfingers.create_fingers(fingerType,
                                         float(tabWidth)/10,
                                         float(mtlThick)/10,
                                         startWithTab,
                                         faces,
                                         self.app,
                                         self.ui)

        except:
            uimessage(self.ui, executionFailedMsg, traceback.format_exc())
