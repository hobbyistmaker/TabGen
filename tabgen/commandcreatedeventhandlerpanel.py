import adsk.core
import traceback

from adsk.core import DropDownStyles as dds

from ..util import errorMsgInputId, fingerTypeId, mtlThickInputId
from ..util import selectedFaceInputId, startWithTabInputId
from ..util import tabWidthInputId
from ..util import uimessage
from ..handlers import CommandExecuteHandler, InputChangedHandler
from ..handlers import ValidateInputsHandler

handlers = []

initializedFailedMsg = 'TabGen initialization failed: {}'


class CommandCreatedEventHandlerPanel(adsk.core.CommandCreatedEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui

    def notify(self, args):
        try:
            cmd = args.command
            cmd.helpFile = 'resources/help.html'

            # Add onExecute event handler
            onExecute = CommandExecuteHandler(self.app, self.ui)
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

            # Add onInputChanged handler
            onInputChanged = InputChangedHandler(self.app, self.ui)
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

            # Add onValidateInputs event handler
            onValidateInputs = ValidateInputsHandler(self.app, self.ui)
            cmd.validateInputs.add(onValidateInputs)
            handlers.append(onValidateInputs)

            # Set up the inputs
            commandInputs = cmd.commandInputs
            selComInput = commandInputs.addSelectionInput(
                selectedFaceInputId,
                'Face: ',
                'Faces on which to cut tabs')
            selComInput.addSelectionFilter('PlanarFaces')
            selComInput.setSelectionLimits(0)

            boxtypedropdown = commandInputs.addDropDownCommandInput(fingerTypeId, 'Fingers Type', dds.TextListDropDownStyle)
            boxtypedropdownitems = boxtypedropdown.listItems
            boxtypedropdownitems.add('User-Defined Width', True, '')
            boxtypedropdownitems.add('Automatic Width', False, '')

            commandInputs.addFloatSpinnerCommandInput(tabWidthInputId, 'Tab Width: ', 'mm', 2.0, 20.0, 0.1, 8.0)
            commandInputs.addFloatSpinnerCommandInput(mtlThickInputId, 'Material Thickness: ', 'mm', 0.5, 6.0, 0.1, 3.0)
            commandInputs.addBoolValueInput(startWithTabInputId, 'Start with tab: ', True)
            commandInputs.addTextBoxCommandInput(errorMsgInputId, '', '', 2, True)

        except:
            uimessage(self.ui, initializedFailedMsg, traceback.format_exc())
