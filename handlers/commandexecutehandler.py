import traceback

from adsk.core import Application
from adsk.core import CommandEventHandler

app = Application.get()
ui = app.userInterface

# Constants
executionFailedMsg = 'TabGen executon failed: {}'


class CommandExecuteHandler(CommandEventHandler):

    def __init__(self, generator):
        super().__init__()
        self.generator = generator

    def notify(self, args):
        command = args.firingEvent.sender

        try:

            self.generator.create(command.commandInputs)

        except:

            ui.messageBox(executionFailedMsg.format(traceback.format_exc()))
