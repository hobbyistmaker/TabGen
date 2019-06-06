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
            first_inputs = args.inputs
            parent_inputs = args.inputs.command.commandInputs if args.inputs.command else first_inputs
            inputs = fusion.ChangedInputs(parent_inputs)

            id_ = cmdInput.id

            if id_ == defs.fingerPlaceId:
                inputs.finger_placement()

            if id_ == defs.selectedFaceInputId or id_ == defs.fingerPlaceId:
                inputs.find_opposite()

            if id_ in [defs.selectedFaceInputId,
                       defs.dualEdgeSelectId,
                       defs.fingerPlaceId
                       ]:
                inputs.update_inputs()

        except:
            self.ui.messageBox(traceback.format_exc(3))
