import traceback

from collections import namedtuple

from adsk.core import CommandCreatedEventHandler
from adsk.core import DropDownStyles as dds

from .. import definitions as defs
from .commandexecutehandler import CommandExecuteHandler
from .commandexecutepreviewhandler import CommandExecutePreviewHandler
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
            design = self.app.activeProduct
            units_manager = design.unitsManager
            units = units_manager.defaultLengthUnits

            if document.isSaved is not True:
                self.ui.messageBox('Please save your document before continuing.')

            else:
                cmd = args.command
                # cmd.helpFile = 'resources/help.html'
                cmd.helpFile = self.config.help_file

                # Add onExecute event handler
                execute = CommandExecuteHandler(self.config)
                cmd.execute.add(execute)
                self.handlers.append(execute)

                # Add onExecute event handler
                execute_preview = CommandExecutePreviewHandler(self.config)
                cmd.executePreview.add(execute_preview)
                self.handlers.append(execute_preview)

                # Add onInputChanged handler
                changed = InputChangedHandler(self.app, self.ui)
                cmd.inputChanged.add(changed)
                self.handlers.append(changed)

                # # Add onValidateInputs event handler
                # validate = ValidateInputsHandler(self.app, self.ui)
                # cmd.validateInputs.add(validate)
                # self.handlers.append(validate)

                # Add SelectionEvent handler
                selection = SelectionEventHandler(self.app, self.ui)
                cmd.selectionEvent.add(selection)
                self.handlers.append(selection)

                # Set up the inputs
                cmd_inputs = cmd.commandInputs

                main_input = cmd_inputs.addTabCommandInput('mainTabInput', 'Main')
                inputs = main_input.children

                self.add_dropdown(inputs, defs.fingerTypeId, 'Fingers Type', [Item(defs.userDefinedWidthId,
                                                                                   self.config.DEFAULT_USER_WIDTH_TAB),
                                                                              Item(defs.automaticWidthId,
                                                                                   self.config.DEFAULT_AUTO_WIDTH_TAB)]
                                                                              )

                self.add_dropdown(inputs, defs.fingerPlaceId, 'Placement', [Item(defs.singleEdgeId,
                                                                                 self.config.DEFAULT_SINGLE_EDGE),
                                                                            Item(defs.dualEdgeId,
                                                                                 self.config.DEFAULT_DUAL_EDGE)
                                                                            ])

                self.add_selection(inputs, defs.selectedFaceInputId, 'Face', 'Faces where tabs will be cut.',
                                   'PlanarFaces', 1, 1)

                self.add_selection(inputs, defs.dualEdgeSelectId, 'Secondary Face',
                                   'Opposite face for dual-edge cuts.', 'PlanarFaces', 0, 1)

                tcinput = inputs.addIntegerSpinnerCommandInput(defs.wallCountInputId, 'Number of Tabs',
                                                               0, 200, 1, self.config.DEFAULT_TAB_COUNT)

                tcinput.isVisible = False
                tcinput.isEnabled = False

                inputs.addFloatSpinnerCommandInput(
                    defs.tabWidthInputId,
                    'Tab Width',
                    units,
                    units_manager.convert(2.0, 'mm', units),
                    units_manager.convert(20.0, 'mm', units),
                    units_manager.convert(0.1, 'mm', units),
                    units_manager.convert(self.config.DEFAULT_TAB_WIDTH, 'mm', units)
                    )
                inputs.addFloatSpinnerCommandInput(
                    defs.mtlThickInputId,
                    'Tab Depth',
                    units,
                    units_manager.convert(0.5, 'mm', units),
                    units_manager.convert(6.0, 'mm', units),
                    units_manager.convert(0.1, 'mm', units),
                    units_manager.convert(self.config.DEFAULT_MATERIAL_THICKNESS, 'mm', units)
                    )

                inputs.addBoolValueInput(defs.startWithTabInputId,
                                         'Start with tab',
                                         True,
                                         '',
                                         self.config.DEFAULT_START_WITH_TAB)
                inputs.addFloatSpinnerCommandInput(defs.lengthInputId,
                                                   'Face Length',
                                                   units,
                                                   units_manager.convert(0, 'mm', units),
                                                   units_manager.convert(2500.0, 'mm', units),
                                                   units_manager.convert(0.1, 'mm', units),
                                                   units_manager.convert(0.0, 'mm', units))
                inputs.addFloatSpinnerCommandInput(defs.distanceInputId,
                                                   'Duplicate Distance',
                                                   units,
                                                   units_manager.convert(0, 'mm', units),
                                                   units_manager.convert(2500.0, 'mm', units),
                                                   units_manager.convert(0.1, 'mm', units),
                                                   units_manager.convert(0.0, 'mm', units))

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
                inputs.addBoolValueInput(defs.previewInputId,
                                         'Enable Preview',
                                         True,
                                         '',
                                         self.config.DEFAULT_ENABLE_PREVIEW)

                tab_inputs = cmd_inputs.addTabCommandInput(defs.advancedTabId, 'Advanced').children

                tab_inputs.addIntegerSpinnerCommandInput(defs.wallCountInputId, 'Interior Walls',
                                                     0, 200, 1, self.config.DEFAULT_WALL_COUNT)

                tab_inputs.addFloatSpinnerCommandInput(
                    defs.marginInputId,
                    'Margin from Sides',
                    units,
                    units_manager.convert(0, 'mm', units),
                    units_manager.convert(2500, 'mm', units),
                    units_manager.convert(0.1, 'mm', units),
                    units_manager.convert(self.config.DEFAULT_MARGIN_WIDTH, 'mm', units)
                    )

                tab_inputs.addFloatSpinnerCommandInput(
                    defs.edgeMarginInputId,
                    'Margin from Edge',
                    units,
                    units_manager.convert(0, 'mm', units),
                    units_manager.convert(2500, 'mm', units),
                    units_manager.convert(0.1, 'mm', units),
                    units_manager.convert(self.config.DEFAULT_MARGIN_WIDTH, 'mm', units)
                    )

                tab_inputs.addFloatSpinnerCommandInput(
                    defs.kerfInputId,
                    'Kerf Adjustment',
                    units,
                    units_manager.convert(0, 'mm', units),
                    units_manager.convert(50.8, 'mm', units),
                    units_manager.convert(0.1, 'mm', units),
                    units_manager.convert(self.config.DEFAULT_KERF_WIDTH, 'mm', units)
                    )

        except:
            self.ui.messageBox('{}:\n{}'.format(initializedFailedMsg,
                                                traceback.format_exc(3)))
