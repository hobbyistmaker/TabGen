import adsk.core
import traceback

from ..tabgen import TabConfig
from ..tabgen import FingerFace
from ..util import uimessage
from ..util import mtlThickInputId
from ..util import (fingerTypeId,
                    selectedFaceInputId,
                    startWithTabInputId,
                    tabWidthInputId,
                    dualSidesInputId,
                    dualEdgeSelectId,
                    parametricInputId)


# Constants
executionFailedMsg = 'TabGen executon failed: {}'


def get_edge(selection, ui=None):
    if selection is None or selection.selectionCount == 0:
        return None
    return selection.selection(0).entity


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

            finger_type = commandInputs.itemById(fingerTypeId).selectedItem.name
            tab_width = commandInputs.itemById(tabWidthInputId).value
            depth = commandInputs.itemById(mtlThickInputId).value
            edge_input = commandInputs.itemById(dualEdgeSelectId)

            edge = get_edge(edge_input, self.ui)
            parametric = commandInputs.itemById(parametricInputId).value
            # start_tab = commandInputs.itemById(startWithTabInputId).value
            # Starting without a tab opens up multiple bugs that need to be solved
            # Disable for now
            start_tab = True

            tab_config = TabConfig(finger_type, tab_width, depth,
                                   start_tab, edge, parametric)

            faces = [FingerFace(selInput.selection(j).entity, self.ui)
                     for j in range(selInput.selectionCount)]

            for face in faces:
                face.create_fingers(tab_config)

        except:
            uimessage(self.ui, executionFailedMsg, traceback.format_exc())
