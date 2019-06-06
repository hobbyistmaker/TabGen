import traceback

from adsk.core import ValidateInputsEventHandler

from .. import fusion

validateFailedMsg = 'TabGen validate inputs failed: {}'


class InputValidationError(Exception): pass


def check_edge(inputs):
    if not inputs.selected_face:
        return False

    return fusion.check_if_edge(inputs.selected_face)


def check_all(inputs):
    if ((not inputs.face_selected) or
       (inputs.dual_edge_selected and not inputs.edge_selected)):
        return False

    return check_edge(inputs)


class ValidateInputsHandler(ValidateInputsEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui

    def notify(self, args):
        try:
            # Validate that the tabs are being cut on the edge of
            # material and that the face is long enough for at least
            # one tab
            first_inputs = args.inputs
            parent_inputs = args.inputs.command.commandInputs if args.inputs.command else first_inputs
            inputs = fusion.InputReader(parent_inputs)
            args.areInputsValid = check_all(inputs)

        except:
            raise InputValidationError(traceback.format_exc(3))
