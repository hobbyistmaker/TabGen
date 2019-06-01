import traceback

from collections import namedtuple

from adsk.core import CommandCreatedEventHandler
from adsk.core import DropDownStyles as dds

from .. import definitions as defs
from .commandexecutehandler import CommandExecuteHandler
from .inputchangedhandler import InputChangedHandler
from .selectioneventhandler import SelectionEventHandler
from .validateinputshandler import ValidateInputsHandler

Item = namedtuple('Item', ['id_', 'enabled'])

initializedFailedMsg = 'TabGen initialization failed: {}'

class CommandCreatedEventHandlerPanel(CommandCreatedEventHandler):

    def __init__(self, config):
        super().__init__()
        self.app = config.app
        self.ui = config.ui
        self.config = config
        self.handlers = []

    def add_dropdown(self, inputs, id_, name, items):
        input_ = inputs.addDropDownCommandInput(id_,
                                                name,
                                                dds.TextListDropDownStyle)
        listItems = input_.listItems
        for item in items:
            listItems.add(item.id_,
                          item.enabled)

    def add_selection(self, inputs, id_, name, help_, filter_, min_, max_):
        input_ = inputs.addSelectionInput(
            id_,
            name,
            help_
            )
        input_.addSelectionFilter(filter_)
        input_.setSelectionLimits(min_, max_)

    def notify(self, args):
        try:
            document = self.app.activeDocument
            if document.isSaved is not True:
                self.ui.messageBox('Please save your document before continuing.')

            else:
                cmd = args.command
                cmd.helpFile = 'resources/help.html'

                # Add onExecute event handler
                execute = CommandExecuteHandler(self.app, self.ui)
                cmd.execute.add(execute)
                self.handlers.append(execute)

                # Add onInputChanged handler
                changed = InputChangedHandler(self.app, self.ui)
                cmd.inputChanged.add(changed)
                self.handlers.append(changed)

                # Add onValidateInputs event handler
                validate = ValidateInputsHandler(self.app, self.ui)
                cmd.validateInputs.add(validate)
                self.handlers.append(validate)

                # Add SelectionEvent handler
                selection = SelectionEventHandler(self.app, self.ui)
                cmd.selectionEvent.add(selection)
                self.handlers.append(selection)

                # Set up the inputs
                inputs = cmd.commandInputs

                self.add_dropdown(
                    inputs,
                    defs.fingerTypeId,
                    'Fingers Type',
                    [Item(defs.userDefinedWidthId,
                          self.config.DEFAULT_USER_WIDTH_TAB),
                    Item(defs.automaticWidthId,
                         self.config.DEFAULT_AUTO_WIDTH_TAB)
                    ])

                self.add_dropdown(
                    inputs,
                    defs.fingerPlaceId,
                    'Placement',
                    [Item(defs.singleEdgeId,
                          self.config.DEFAULT_SINGLE_EDGE),
                     Item(defs.dualEdgeId,
                          self.config.DEFAULT_DUAL_EDGE)
                    ])

                self.add_selection(
                    inputs,
                    defs.selectedFaceInputId,
                    'Face',
                    'Faces where tabs will be cut.',
                    'PlanarFaces',
                    1,
                    1
                )

                self.add_selection(
                    inputs,
                    defs.dualEdgeSelectId,
                    'Duplicate Edge',
                    'Edge on opposite side for dual-edge cuts.',
                    'LinearEdges',
                    0,
                    1
                )

                inputs.addIntegerSpinnerCommandInput(
                    defs.wallCountInputId,
                    'Interior Walls',
                    0,
                    200,
                    1,
                    self.config.DEFAULT_WALL_COUNT
                    )

                inputs.addFloatSpinnerCommandInput(
                    defs.tabWidthInputId,
                    'Tab Width',
                    'mm',
                    2.0,
                    20.0,
                    0.1,
                    self.config.DEFAULT_TAB_WIDTH
                    )
                inputs.addFloatSpinnerCommandInput(
                    defs.mtlThickInputId,
                    'Tab Depth',
                    'mm',
                    0.5,
                    6.0,
                    0.1,
                    self.config.DEFAULT_MATERIAL_THICKNESS
                    )
                inputs.addFloatSpinnerCommandInput(
                    defs.marginInputId,
                    'Margin from Edge',
                    'mm',
                    0,
                    2500,
                    0.1,
                    self.config.DEFAULT_MARGIN_WIDTH
                    )

                # Disable start with tab due to bugs
                inputs.addBoolValueInput(defs.startWithTabInputId,
                                         'Start with tab',
                                         True,
                                         '',
                                         self.config.DEFAULT_START_WITH_TAB)
                inputs.addFloatSpinnerCommandInput(defs.lengthInputId,
                                                   'Face Length',
                                                   'mm',
                                                   0,
                                                   2500.0,
                                                   0.1,
                                                   0.0)
                inputs.addFloatSpinnerCommandInput(defs.distanceInputId,
                                                   'Duplicate Distance',
                                                   'mm',
                                                   0,
                                                   2500.0,
                                                   0.1,
                                                   0.0)

                inputs.addTextBoxCommandInput(defs.ERROR_MSG_INPUT_ID,
                                              '',
                                              '',
                                              2,
                                              True)

                inputs.addBoolValueInput(defs.parametricInputId,
                                         'Disable Parametric',
                                         True,
                                         '',
                                         self.config.DEFAULT_DISABLE_PARAMETRIC)
        except:
            self.ui.messageBox('{}:\n{}'.format(initializedFailedMsg,
                                                traceback.format_exc(3)))
