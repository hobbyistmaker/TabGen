import adsk.core
import traceback

from adsk.core import DropDownStyles as dds

from ..util import distanceInputId
from ..util import dualEdgeId
from ..util import dualEdgeSelectId
from ..util import errorMsgInputId
from ..util import fingerTypeId
from ..util import fingerPlaceId
from ..util import lengthInputId
from ..util import mtlThickInputId
from ..util import parametricInputId
from ..util import selectedFaceInputId
from ..util import singleEdgeId
from ..util import startWithTabInputId
from ..util import tabWidthInputId
from ..util import uimessage
from .commandexecutehandler import CommandExecuteHandler
from .inputchangedhandler import InputChangedHandler
from .validateinputshandler import ValidateInputsHandler
from .selectioneventhandler import SelectionEventHandler

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
            onValidateInputs = ValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            handlers.append(onValidateInputs)

            # Add SelectionEvent handler
            onSelectionEvent = SelectionEventHandler()
            cmd.selectionEvent.add(onSelectionEvent)
            handlers.append(onSelectionEvent)

            # Set up the inputs
            commandInputs = cmd.commandInputs

            boxtypedropdown = commandInputs.addDropDownCommandInput(fingerTypeId, 'Fingers Type', dds.TextListDropDownStyle)
            boxtypedropdownitems = boxtypedropdown.listItems
            boxtypedropdownitems.add('User-Defined Width', False, '')
            boxtypedropdownitems.add('Automatic Width', True, '')

            placedropdown = commandInputs.addDropDownCommandInput(fingerPlaceId, 'Placement', dds.TextListDropDownStyle)
            placedropdownitems = placedropdown.listItems
            placedropdownitems.add(singleEdgeId, False, '')
            placedropdownitems.add(dualEdgeId, True, '')

            selComInput = commandInputs.addSelectionInput(
                selectedFaceInputId,
                'Face: ',
                'Faces on which to cut tabs')
            selComInput.addSelectionFilter('PlanarFaces')
            selComInput.setSelectionLimits(1, 1)

            edgeComInput = commandInputs.addSelectionInput(
                dualEdgeSelectId,
                'Duplicate Face: ',
                'Edge to use for distance to opposite side')
            # edgeComInput.addSelectionFilter('PlanarFaces')
            edgeComInput.addSelectionFilter('LinearEdges')
            edgeComInput.setSelectionLimits(0, 1)

            commandInputs.addFloatSpinnerCommandInput(tabWidthInputId, 'Tab Width: ', 'mm', 2.0, 20.0, 0.1, 8.0)
            commandInputs.addFloatSpinnerCommandInput(mtlThickInputId, 'Material Thickness: ', 'mm', 0.5, 6.0, 0.1, 3.0)
            # Disable start with tab due to bugs
            commandInputs.addBoolValueInput(startWithTabInputId, 'Start with tab: ', True, '', True)
            commandInputs.addBoolValueInput(parametricInputId, 'Make Parametric: ', True, '', True)
            commandInputs.addFloatSpinnerCommandInput(lengthInputId, 'Length Parameter: ', 'mm', -2500.0, 2500.0, 0.1, 0.0)
            commandInputs.addFloatSpinnerCommandInput(distanceInputId, 'Distance Parameter: ', 'mm', -2500.0, 2500.0, 0.1, 0.0)
            # commandInputs.addFloatSpinnerCommandInput(distanceInputId, 'Distance Parameter: ', 'mm', 2.0, 20.0, 0.1, 1.0)

            commandInputs.addTextBoxCommandInput(errorMsgInputId, '', '', 2, True)

        except:
            uimessage(initializedFailedMsg, traceback.format_exc())
