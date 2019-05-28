import math
import traceback

from adsk.core import Application
from adsk.fusion import Design

# app = Application.get()
# ui = app.userInterface
# des = Design.cast(app.activeProduct)


class Base:

    app = Application.get()
    ui = app.userInterface

    @classmethod
    def distance(cls, a, b):
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)

    @classmethod
    def clean_string(cls, param):
        for ch in [' ', '-', '(', ')']:
            if ch in param:
                param = param.replace(ch, '_')
        return param.lower()

    @classmethod
    def msg(cls, value):
        cls.ui.messageBox(value)

    @classmethod
    def trace(cls, value):
        cls.ui.messageBox('{}:\n{}'.format(value if value else '', traceback.format_exc()))

    @property
    def design(self):
        return Design.cast(self.app.activeProduct)

    @property
    def design_parameters(self):
        return self.design.allParameters

    @property
    def user_parameters(self):
        return self.design.userParameters
