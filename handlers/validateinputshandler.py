import adsk.core
import traceback

from ..util import uimessage
from ..util import errorMsgInputId  # , mtlThickInputId
from ..util import selectedFaceInputId, tabWidthInputId

validateFailedMsg = 'TabGen validate inputs failed: {}'

tolerance = .001


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
            selInput = commandInputs.itemById(selectedFaceInputId)

            faces = [selInput.selection(j).entity
                     for j in range(selInput.selectionCount)]

            tabWidth = commandInputs.itemById(tabWidthInputId).value
            # mtlThick = commandInputs.itemById(mtlThickInputId).value
            errMsg = commandInputs.itemById(errorMsgInputId)
            e1 = ''
            e2 = ''

            for face in faces:
                pRange = face.evaluator.parametricRange()
                dimA = abs(pRange.maxPoint.x - pRange.minPoint.x)
                dimB = abs(pRange.maxPoint.y - pRange.minPoint.y)

                # Disabled the edge check for now. It's not valid.
                # This should be checking the dimensions of the body,
                # not comparing the user-entered material thickness to the
                # dimensions

                # if (abs(dimA - mtlThick) > tolerance
                #         and abs(dimB - mtlThick) > tolerance):
                #     e1 = 'Can only cut tabs on the edge of material.'
                #     args.areInputsValid = False

                # This check will eventually need to be made more
                # robust.

                if dimA < 2 * tabWidth and dimB < 2 * tabWidth:
                    e2 = 'Edges must be at least 2 * the tab width.'
                    args.areInputsValid = False

            errMsg.text = e1 + '\n' + e2

        except:
            uimessage(self.ui, validateFailedMsg, traceback.format_exc())
