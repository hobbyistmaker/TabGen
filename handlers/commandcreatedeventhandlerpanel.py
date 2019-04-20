import adsk.core
import traceback

from adsk.core import DropDownStyles as dds

from ..util import errorMsgInputId, fingerTypeId, mtlThickInputId
from ..util import selectedFaceInputId, startWithTabInputId
from ..util import tabWidthInputId, dualEdgeSelectId
from ..util import parametricInputId
from ..util import uimessage
from .commandexecutehandler import CommandExecuteHandler
from .inputchangedhandler import InputChangedHandler
from .validateinputshandler import ValidateInputsHandler

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
            selComInput.setSelectionLimits(1, 1)

            boxtypedropdown = commandInputs.addDropDownCommandInput(fingerTypeId, 'Fingers Type', dds.TextListDropDownStyle)
            boxtypedropdownitems = boxtypedropdown.listItems
            boxtypedropdownitems.add('User-Defined Width', False, '')
            boxtypedropdownitems.add('Automatic Width', True, '')

            edgeComInput = commandInputs.addSelectionInput(
                dualEdgeSelectId,
                'Duplicate Edge: ',
                'Edge to use for distance to opposite side')
            edgeComInput.addSelectionFilter('LinearEdges')
            edgeComInput.setSelectionLimits(0, 1)

            commandInputs.addFloatSpinnerCommandInput(tabWidthInputId, 'Tab Width: ', 'mm', 2.0, 20.0, 0.1, 8.0)
            commandInputs.addFloatSpinnerCommandInput(mtlThickInputId, 'Material Thickness: ', 'mm', 0.5, 6.0, 0.1, 3.0)
            # Disable start with tab due to bugs
            # commandInputs.addBoolValueInput(startWithTabInputId, 'Start with tab: ', True, '', True)
            commandInputs.addBoolValueInput(parametricInputId, 'Make Parametric: ', True, '', True)
            commandInputs.addTextBoxCommandInput(errorMsgInputId, '', '', 2, True)

        except:
            uimessage(self.ui, initializedFailedMsg, traceback.format_exc())
