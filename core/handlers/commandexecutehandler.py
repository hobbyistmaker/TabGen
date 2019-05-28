import traceback

from adsk.core import CommandEventHandler

from .. import fusion
from .. import managers

# Constants
executionFailedMsg = 'TabGen executon failed: {}'


class CommandExecuteHandler(CommandEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui

    def notify(self, args):
        command = args.firingEvent.sender

        try:
            inputs = fusion.InputReader(command.commandInputs)
            manager = managers.create(self.app, self.ui, inputs)

            self.ui.messageBox('Executing command.')

        except:

            self.ui.messageBox(executionFailedMsg.format(traceback.format_exc()))
