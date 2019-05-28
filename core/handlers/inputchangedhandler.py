import traceback

from adsk.core import Application
from adsk.core import InputChangedEventHandler

from .. import fusion
from .. import definitions as defs

# Constants

eventFailedMsg = 'TabGen input changed event failed: {}'

class InputChangeValidationError(Exception): pass


class InputChangedHandler(InputChangedEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui

    def notify(self, args):
        try:
            cmdInput = args.input
            inputs = fusion.ChangedInputs(args.inputs)

            id_ = cmdInput.id

            if id_ == defs.fingerPlaceId:
                inputs.finger_placement()

            if id_ in [defs.selectedFaceInputId,
                       defs.dualEdgeSelectId,
                       defs.fingerPlaceId
                       ]:
                inputs.update_inputs()

        except:
            self.ui.messageBox(traceback.format_exc(3))
