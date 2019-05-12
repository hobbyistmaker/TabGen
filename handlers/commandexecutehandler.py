import adsk.core
import traceback

from ..core import Face
from ..core import Fingers
from ..core import TabConfig

app = adsk.core.Application.get()
ui = app.userInterface

# Constants
executionFailedMsg = 'TabGen executon failed: {}'


class CommandExecuteHandler(adsk.core.CommandEventHandler):

    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:

            command = args.firingEvent.sender
            commandInputs = command.commandInputs

            face = Face.from_inputs(commandInputs)
            fingers = Fingers.create(face, commandInputs)

        except:

            ui.messageBox(executionFailedMsg.format(traceback.format_exc()))

