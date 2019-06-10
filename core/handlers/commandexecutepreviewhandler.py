import traceback

from adsk.core import CommandEventHandler

from .. import fusion
from .. import managers

# Constants
executionFailedMsg = 'TabGen executon failed: {}'


class CommandExecutePreviewHandler(CommandEventHandler):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.ui = self.config.ui
        self.app = self.config.app

    def notify(self, args):
        command = args.firingEvent.sender

        try:
            first_inputs = command.commandInputs
            parent_inputs = first_inputs.command.commandInputs if first_inputs.command else first_inputs
            inputs = fusion.InputReader(self.app, parent_inputs)
            properties = inputs.create_properties(self.app, self.ui)

            if inputs.preview_enabled:

                if inputs.dual_edge_selected and inputs.face_selected and inputs.edge_selected:
                    managers.create(inputs, properties, preview=True)
                elif inputs.single_edge_selected and inputs.face_selected:
                    managers.create(inputs, properties, preview=True)

                if inputs.parametric:
                    args.isValidResult = True
                else:
                    args.isValidResult = False
            else:
                args.isValidResult = False

        except:

            self.ui.messageBox(executionFailedMsg.format(traceback.format_exc()))
