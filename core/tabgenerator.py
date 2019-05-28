import logging

from collections import namedtuple

from adsk.core import DropDownStyles as dds

from .handlers import CommandCreatedEventHandlerPanel
from .handlers import CommandExecuteHandler
from .handlers import InputChangedHandler

from . import definitions as defs

logger = logging.getLogger('tabgen')


class TabGenerator:

    def start(self, app, ui, config, context):
        self.app = app
        self.ui = ui
        self.config = config
        self.handlers = []

    def stop(self):
        if self.control:
            self.control.deleteMe()

        if self.command:
            self.command.deleteMe()

    def create_panel(self, args):

