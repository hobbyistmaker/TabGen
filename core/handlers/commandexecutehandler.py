import traceback

from adsk.core import CommandEventHandler

from .. import fusion
from .. import managers

# Constants
executionFailedMsg = 'TabGen executon failed: {}'


class CommandExecuteHandler(CommandEventHandler):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.ui = self.config.ui

    def notify(self, args):
        command = args.firingEvent.sender

        try:
            self.config.inputs = fusion.InputReader(command.commandInputs)

            if self.config.inputs.face_selected:
                managers.create(self.config, preview=False)
            else:
                self.ui.messageBox('No face was selected for placing fingers.')

        except:

            self.ui.messageBox(executionFailedMsg.format(traceback.format_exc()))
