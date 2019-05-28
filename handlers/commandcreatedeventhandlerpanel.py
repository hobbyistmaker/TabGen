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
from ..util import marginInputId
from ..util import mtlThickInputId
from ..util import parametricInputId
from ..util import selectedFaceInputId
from ..util import singleEdgeId
from ..util import startWithTabInputId
from ..util import tabWidthInputId
from ..util import userDefinedWidthId
from ..util import automaticWidthId
from ..config import Configuration

app = Application.get()
ui = app.userInterface

handlers = []

initializedFailedMsg = 'TabGen initialization failed: {}'
logger = logging.getLogger('commandcreatedeventhandlerpanel')


class CommandCreatedEventHandlerPanel(adsk.core.CommandCreatedEventHandler):

    def __init__(self, execute, input_, validate, select):
        super().__init__()

        self.execute = execute
        self.input_ = input_
        self.validate = validate
        self.select = select

    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface

            document = app.activeDocument
            if document.isSaved is not True:
                ui.messageBox('Please save your document before continuing.')

            else:
                logger.debug('Creating {}.'.format(self.__class__.__name__.lower()))
                cmd = args.command
                cmd.helpFile = 'resources/help.html'


                # Add onExecute event handler
                cmd.execute.add(self.execute)

                # Add onInputChanged handler
                cmd.inputChanged.add(self.input_)

                # # Add onValidateInputs event handler
                # cmd.validateInputs.add(self.validate)

                # Add SelectionEvent handler
                cmd.selectionEvent.add(self.select)

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
                commandInputs.addFloatSpinnerCommandInput(marginInputId,
                                                          'Margin from Edge: ', 'mm',
                                                          0, 2500, 0.1,
                                                          Configuration.DEFAULT_MATERIAL_THICKNESS)

                # Disable start with tab due to bugs
                commandInputs.addBoolValueInput(startWithTabInputId, 'Start with tab: ', True, '', Configuration.DEFAULT_START_WITH_TAB)
                logger.debug('Created Start With Tab boolean check with default value of {}'.format(Configuration.DEFAULT_START_WITH_TAB))
                commandInputs.addBoolValueInput(parametricInputId, 'Make Parametric: ', True, '', Configuration.DEFAULT_MAKE_PARAMETRIC)
                logger.debug('Created Make Parametric boolean check with default value of {}'.format(Configuration.DEFAULT_MAKE_PARAMETRIC))
                commandInputs.addFloatSpinnerCommandInput(lengthInputId, 'Length Parameter: ', 'mm', 0, 2500.0, 0.1, 0.0)
                commandInputs.addFloatSpinnerCommandInput(distanceInputId, 'Distance Parameter: ', 'mm', 0, 2500.0, 0.1, 0.0)

                commandInputs.addTextBoxCommandInput(errorMsgInputId, '', '', 2, True)
        except:
            ui.messageBox('{}:\n{}'.format(initializedFailedMsg, traceback.format_exc(3)))
