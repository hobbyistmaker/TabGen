import math
import traceback

from adsk.core import Application
from adsk.fusion import Design

app = Application.get()
ui = app.userInterface
des = Design.cast(app.activeProduct)


class Base:

    def __init__(self):
        self.app = app
        self.ui = ui
        self.design  = des

    def distance(self, a, b):
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)

    def clean_string(self, param):
        for ch in [' ', '-', '(', ')']:
            if ch in param:
                param = param.replace(ch, '_')
        return param.lower()

    def msg(self, value):
        self.ui.messageBox(value)

    @classmethod
    def trace(cls, value):
        ui.messageBox('{}:\n{}'.format(value if value else '', traceback.format_exc()))
