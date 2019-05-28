import traceback

from adsk.core import Application
from adsk.core import ValidateInputsEventHandler

from ..util import distanceInputId
from ..util import lengthInputId
from ..util import errorMsgInputId
from ..util import fingerTypeId
from ..util import marginInputId
from ..util import mtlThickInputId
from ..util import selectedFaceInputId
from ..util import startWithTabInputId
from ..util import tabWidthInputId
from ..util import dualEdgeSelectId
from ..util import parametricInputId
from ..util import automaticWidthId
from ..util import userDefinedWidthId

from ..core import Face
from ..core import Body

app = Application.get()
ui = app.userInterface

validateFailedMsg = 'TabGen validate inputs failed: {}'


def check_params(args,  err_msg):
    err_msg.text = ''

    face = args.inputs.itemById(selectedFaceInputId).selection(0).entity

    if face:
        body = Body.from_face(face)

        if body.is_edge(face):
            return True

    return False


class ValidateInputsHandler(ValidateInputsEventHandler):

    def notify(self, args):
        try:
            # Validate that the tabs are being cut on the edge of
            # material and that the face is long enough for at least
            # one tab
            commandInputs = args.inputs
            errMsg = commandInputs.itemById(errorMsgInputId)
            args.areInputsValid = check_params(args, errMsg)

        except:
            ui.messageBox(validateFailedMsg.format(traceback.format_exc()))
