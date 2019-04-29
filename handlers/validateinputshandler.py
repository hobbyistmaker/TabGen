import adsk.core
import traceback

from ..tabgen import TabConfig
from ..util import distanceInputId
from ..util import lengthInputId
from ..util import uimessage
from ..util import errorMsgInputId
from ..util import fingerTypeId
from ..util import mtlThickInputId
from ..util import selectedFaceInputId
from ..util import startWithTabInputId
from ..util import tabWidthInputId
from ..util import dualEdgeSelectId
from ..util import parametricInputId
from ..util import automaticWidthId
from ..util import userDefinedWidthId

from ..tabgen import FingerFace

validateFailedMsg = 'TabGen validate inputs failed: {}'

tolerance = .001


def check_params(args, tab_config, selected_face, selected_edge, err_msg):
    app = adsk.core.Application.get()
    ui = app.userInterface

    document = app.activeDocument
    if document.isSaved is not True:
        ui.messageBox('Please save your document before continuing.')
        return False

    tab_width = tab_config.default_width
    err_msg.text = ''

    if selected_face.selectionCount > 0:
        faces = [FingerFace.create(automaticWidthId,
                                   selected_face.selection(j).entity,
                                   tab_config)
                 for j in range(selected_face.selectionCount)]

        small = False
        for face in faces:
            pRange = face.evaluator.parametricRange()
            dimA = abs(pRange.maxPoint.x - pRange.minPoint.x)
            dimB = abs(pRange.maxPoint.y - pRange.minPoint.y)

            if dimA < 2 * tab_width and dimB < 2 * tab_width:
                err_msg.text = 'Edges must be at least 2 * the tab width.\n'
                small = True

            if not face.is_edge:
                err_msg.text = 'TabGen will not operate on non-edge faces.'
                return False

        if small:
            return False

        if tab_config.finger_type == userDefinedWidthId and tab_config.start_with_tab is False:
            err_msg.text = 'Starting without tabs using user-defined width is currently not supported.\n'
            # return False

        return True
    else:
        return False


class ValidateInputsHandler(adsk.core.ValidateInputsEventHandler):

    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # Validate that the tabs are being cut on the edge of
            # material and that the face is long enough for at least
            # one tab
            commandInputs = args.inputs
            errMsg = commandInputs.itemById(errorMsgInputId)

            finger_type = commandInputs.itemById(fingerTypeId).selectedItem.name
            tab_width = commandInputs.itemById(tabWidthInputId).value
            parametric = commandInputs.itemById(parametricInputId).value
            start_tab = commandInputs.itemById(startWithTabInputId).value
            depth = commandInputs.itemById(mtlThickInputId).value

            selInput = commandInputs.itemById(selectedFaceInputId)
            edgeInput = commandInputs.itemById(dualEdgeSelectId)
            length = commandInputs.itemById(lengthInputId)
            distance = commandInputs.itemById(distanceInputId)

            tab_config = TabConfig(finger_type, tab_width,
                                   depth, start_tab, edgeInput,
                                   parametric, length, distance)

            if check_params(args, tab_config, selInput, edgeInput,
                            errMsg):
                args.areInputsValid = True
            else:
                args.areInputsValid = False

        except:
            uimessage(validateFailedMsg, traceback.format_exc())
