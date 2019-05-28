from adsk.core import Application

from ..handlers import CommandExecuteHandler
from ..handlers import InputChangedHandler
from ..handlers import ValidateInputsHandler
from ..handlers import SelectionEventHandler
from ..handlers import CommandCreatedEventHandlerPanel
from ..util import tabGenCommandId
from .tabconfig import UserOptions
from .fingers import Fingers


class TabGeneratorCommandDefinitionException(Exception):
    pass

class TabGeneratorControlDefinitionException(Exception):
    pass

class TabGeneratorPanelException(Exception):
    pass


class TabGenerator:

    def __new__(cls):
        if not hasattr(TabGenerator, 'instance'):
            TabGenerator.instance = super(TabGenerator,cls).__new__(cls)

        return TabGenerator.instance

    def __init__(self):
        self.handlers = []
        self.app = Application.get()
        self.ui = self.app.userInterface

    def create(self, inputs):
        options = UserOptions.create(inputs)
        manager = Fingers.create(options)

    def find_control(self, panel, cmd):
        if not panel:
            raise TabGeneratorPanelException

        try:
            control = panel.controls.itemById(tabGenCommandId)
            return control if control else panel.controls.addCommand(cmd)
        except:
            raise TabGeneratorControlDefinitionException

    def find_command(self, ui):
        if not ui:
            raise TabGeneratorPanelException

        try:
            cmd = self.ui.commandDefinitions.itemById(tabGenCommandId)
            if cmd:
                return cmd
            else:
                return self.ui.commandDefinitions.addButtonDefinition(
                    tabGenCommandId,
                    'Generate Tabs',
                    'Creates finger-joint tabs and gaps on rectangular faces')
        except:
            raise TabGeneratorCommandDefinitionException

    def start(self):
        panel = self.ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cmd = self.find_command(self.ui)
        control = self.find_control(panel, cmd)

        onExecute = CommandExecuteHandler(self)
        self.handlers.append(onExecute)

        onInputChanged = InputChangedHandler()
        self.handlers.append(onInputChanged)

        onValidateInputs = ValidateInputsHandler()
        self.handlers.append(onValidateInputs)

        onSelectionEvent = SelectionEventHandler()
        self.handlers.append(onSelectionEvent)

        onCommandCreated = CommandCreatedEventHandlerPanel(onExecute,
                                                           onInputChanged,
                                                           onValidateInputs,
                                                           onSelectionEvent)

        cmd.commandCreated.add(onCommandCreated)
        self.handlers.append(onCommandCreated)

        if context['IsApplicationStartup'] is False:
            self.ui.messageBox('The "Generate Tabs" command has been added\nto the MODIFY panel of the MODEL workspace.')

    def stop(self):
        panel = self.ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        control = panel.controls.itemById(tabGenCommandId)
        cmd = self.ui.commandDefinitions.itemById(tabGenCommandId)

        if control:
            control.deleteMe()
        if cmd:
            cmd.deleteMe()
