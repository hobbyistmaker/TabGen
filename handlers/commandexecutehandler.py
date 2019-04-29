import adsk.core
import traceback

from ..tabgen import TabConfig
from ..tabgen import FingerFace
from ..util import distanceInputId
from ..util import dualEdgeSelectId
from ..util import fingerTypeId
from ..util import lengthInputId
from ..util import mtlThickInputId
from ..util import parametricInputId
from ..util import selectedFaceInputId
from ..util import startWithTabInputId
from ..util import tabWidthInputId
from ..util import uimessage


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
            tab_width = commandInputs.itemById(tabWidthInputId)
            depth = commandInputs.itemById(mtlThickInputId)
            edge_input = commandInputs.itemById(dualEdgeSelectId)

            edge = get_edge(edge_input, self.ui)
            parametric = commandInputs.itemById(parametricInputId).value
            length_param = commandInputs.itemById(lengthInputId)
            distance = commandInputs.itemById(distanceInputId)

            start_tab = commandInputs.itemById(startWithTabInputId).value

            tab_config = TabConfig(finger_type, tab_width, depth,
                                   start_tab, edge, parametric,
                                   length_param, distance)

            faces = [FingerFace.create(finger_type, selInput.selection(j).entity,
                                       params=tab_config)
                     for j in range(selInput.selectionCount)]

            for face in faces:
                face.create_fingers()

        except:
            uimessage(executionFailedMsg, traceback.format_exc())
