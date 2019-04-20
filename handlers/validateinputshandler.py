import adsk.core
import traceback

from ..tabgen import TabConfig
from ..util import uimessage
from ..util import errorMsgInputId, fingerTypeId, mtlThickInputId
from ..util import selectedFaceInputId, startWithTabInputId, tabWidthInputId
from ..util import userDefinedWidthId, dualSidesInputId, dualEdgeSelectId

from ..tabgen import FingerFace

validateFailedMsg = 'TabGen validate inputs failed: {}'

tolerance = .001


def check_params(tab_config, selected_face, selected_edge, err_msg, ui=None):
    tab_width = tab_config.default_width

    e1, e2 = ('', '')

    if selected_face.selectionCount > 0:
        faces = [FingerFace(selected_face.selection(j).entity, ui)
                 for j in range(selected_face.selectionCount)]

        small = False
        for face in faces:
            pRange = face.evaluator.parametricRange()
            dimA = abs(pRange.maxPoint.x - pRange.minPoint.x)
            dimB = abs(pRange.maxPoint.y - pRange.minPoint.y)

            if dimA < 2 * tab_width and dimB < 2 * tab_width:
                e2 = 'Edges must be at least 2 * the tab width.'
                err_msg.text = e1 + '\n' + e2
                small = True
        if small:
            return False
        else:
            return True
    else:
        return False


class ValidateInputsHandler(adsk.core.ValidateInputsEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui

    def notify(self, args):
        try:
            # Validate that the tabs are being cut on the edge of
            # material and that the face is long enough for at least
            # one tab
            commandInputs = args.inputs
            errMsg = commandInputs.itemById(errorMsgInputId)

            finger_type = commandInputs.itemById(fingerTypeId).selectedItem.name
            tab_width = commandInputs.itemById(tabWidthInputId).value
            # start_tab = commandInputs.itemById(startWithTabInputId).value
            start_tab = True
            depth = commandInputs.itemById(mtlThickInputId).value
            # dual_sides = False

            selInput = commandInputs.itemById(selectedFaceInputId)
            edgeInput = commandInputs.itemById(dualEdgeSelectId)

            tab_config = TabConfig(finger_type, tab_width,
                                   depth, start_tab, edgeInput)

            e1 = ''
            e2 = ''

            if check_params(tab_config, selInput, edgeInput, errMsg, self.ui):
                args.areInputsValid = True
            else:
                args.areInputsValid = False

        except:
            uimessage(self.ui, validateFailedMsg, traceback.format_exc())
