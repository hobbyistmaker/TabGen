import adsk.core
import traceback

from adsk.core import Application

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

app = Application.get()
ui = app.userInterface

validateFailedMsg = 'TabGen validate inputs failed: {}'

tolerance = .001


def check_params(args,  err_msg):
    err_msg.text = ''

    face = Face.from_inputs(args.inputs)

    if face.is_edge:
        return True
    else:
        err_msg.text = 'TabGen will not operate on non-edge faces.'
        return False


class ValidateInputsHandler(adsk.core.ValidateInputsEventHandler):

    def notify(self, args):
        try:
            # Validate that the tabs are being cut on the edge of
            # material and that the face is long enough for at least
            # one tab
            commandInputs = args.inputs
            errMsg = commandInputs.itemById(errorMsgInputId)

            if check_params(args, errMsg):
                args.areInputsValid = True
            else:
                args.areInputsValid = False

        except:
            ui.messageBox(validateFailedMsg.format(traceback.format_exc()))
