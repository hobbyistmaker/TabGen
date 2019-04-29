import logging

import adsk.core
import traceback

from adsk.core import DropDownStyles as dds
from adsk.core import Application

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
from ..util import userDefinedWidthId
from ..util import automaticWidthId
from ..config import Configuration
from .commandexecutehandler import CommandExecuteHandler
from .inputchangedhandler import InputChangedHandler
from .validateinputshandler import ValidateInputsHandler
from .selectioneventhandler import SelectionEventHandler

app = Application.get()
ui = app.userInterface

handlers = []

initializedFailedMsg = 'TabGen initialization failed: {}'
logger = logging.getLogger('commandcreatedeventhandlerpanel')


class CommandCreatedEventHandlerPanel(adsk.core.CommandCreatedEventHandler):

    def notify(self, args):
        try:
            logger.debug('Creating {}.'.format(self.__class__.__name__.lower()))
            cmd = args.command
            cmd.helpFile = 'resources/help.html'

            # Add onExecute event handler
            onExecute = CommandExecuteHandler(app, ui)
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            logger.debug('CommandExecuteHandler added.')

            # Add onInputChanged handler
            onInputChanged = InputChangedHandler(app, ui)
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)
            logger.debug('InputChangedHandler added.')

            # Add onValidateInputs event handler
            onValidateInputs = ValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            handlers.append(onValidateInputs)
            logger.debug('ValidateInputsHandler added.')

            # Add SelectionEvent handler
            onSelectionEvent = SelectionEventHandler()
            cmd.selectionEvent.add(onSelectionEvent)
            handlers.append(onSelectionEvent)
            logger.debug('SelectionEventHandler added.')

            # Set up the inputs
            commandInputs = cmd.commandInputs

            boxtypedropdown = commandInputs.addDropDownCommandInput(fingerTypeId, 'Fingers Type', dds.TextListDropDownStyle)
            boxtypedropdownitems = boxtypedropdown.listItems
            boxtypedropdownitems.add(userDefinedWidthId, Configuration.DEFAULT_USER_WIDTH_TAB, '')
            boxtypedropdownitems.add(automaticWidthId, Configuration.DEFAULT_AUTO_WIDTH_TAB, '')
            logger.debug('Created Fingers Type drop down box.')

            placedropdown = commandInputs.addDropDownCommandInput(fingerPlaceId, 'Placement', dds.TextListDropDownStyle)
            placedropdownitems = placedropdown.listItems
            placedropdownitems.add(singleEdgeId, Configuration.DEFAULT_SINGLE_EDGE, '')
            placedropdownitems.add(dualEdgeId, Configuration.DEFAULT_DUAL_EDGE, '')
            logger.debug('Created Finger Placement drop down box.')

            selComInput = commandInputs.addSelectionInput(
                selectedFaceInputId,
                'Face: ',
                'Faces on which to cut tabs')
            selComInput.addSelectionFilter('PlanarFaces')
            selComInput.setSelectionLimits(1, 1)
            logger.debug('Created face selection input.')

            edgeComInput = commandInputs.addSelectionInput(
                dualEdgeSelectId,
                'Duplicate Face: ',
                'Edge to use for distance to opposite side')
            # edgeComInput.addSelectionFilter('PlanarFaces')
            edgeComInput.addSelectionFilter('LinearEdges')
            edgeComInput.setSelectionLimits(0, 1)
            logger.debug('Created edge selection input.')

            commandInputs.addFloatSpinnerCommandInput(tabWidthInputId,
                                                      'Tab Width: ', 'mm',
                                                      2.0, 20.0, 0.1,
                                                      Configuration.DEFAULT_TAB_WIDTH)
            logger.debug('Created Tab Width input with default value of {}'.format(Configuration.DEFAULT_TAB_WIDTH))
            commandInputs.addFloatSpinnerCommandInput(mtlThickInputId,
                                                      'Material Thickness: ', 'mm',
                                                      0.5, 6.0, 0.1,
                                                      Configuration.DEFAULT_MATERIAL_THICKNESS)
            logger.debug('Created Material Thickness inpurt with default value of {}'.format(Configuration.DEFAULT_MATERIAL_THICKNESS))

            # Disable start with tab due to bugs
            commandInputs.addBoolValueInput(startWithTabInputId, 'Start with tab: ', True, '', Configuration.DEFAULT_START_WITH_TAB)
            logger.debug('Created Start With Tab boolean check with default value of {}'.format(Configuration.DEFAULT_START_WITH_TAB))
            commandInputs.addBoolValueInput(parametricInputId, 'Make Parametric: ', True, '', Configuration.DEFAULT_MAKE_PARAMETRIC)
            logger.debug('Created Make Parametric boolean check with default value of {}'.format(Configuration.DEFAULT_MAKE_PARAMETRIC))
            commandInputs.addFloatSpinnerCommandInput(lengthInputId, 'Length Parameter: ', 'mm', -2500.0, 2500.0, 0.1, 0.0)
            commandInputs.addFloatSpinnerCommandInput(distanceInputId, 'Distance Parameter: ', 'mm', -2500.0, 2500.0, 0.1, 0.0)

            commandInputs.addTextBoxCommandInput(errorMsgInputId, '', '', 2, True)

        except:
            uimessage(initializedFailedMsg, traceback.format_exc())
