from adsk.core import Application
from adsk.fusion import Design
from adsk.core import ValueInput

app = Application.get()
ui = app.userInterface
des = Design.cast(app.activeProduct)

all_params = des.allParameters
user_params = des.userParameters

createByReal = ValueInput.createByReal
createByString = ValueInput.createByString


def clean_param(param):
    return param.replace(' ', '_').replace('(', '').replace(')', '').lower()


def set_value(name, value, units='cm'):
    inputValue = str(value)
    itemParam = user_params.add(name, createByString(inputValue), units, 'Auto-generated Parameter')
    itemParam.expression = inputValue
    return itemParam


class Parameter:

    def __init__(self, prefix, name, expression, units='cm'):
        self.prefix = prefix if isinstance(prefix, str) else str(prefix)
        self._expression = expression.format(prefix) if isinstance(expression, str) else expression
        self._name = clean_param(name if isinstance(name, str) else str(name))
        self._units = units if isinstance(units, str) else ''

        self._param = user_params.itemByName(self.name)
        if not (self._param):
            self._param = self.create()

    @property
    def name(self):
        return clean_param('{0}_{1}'.format(self.prefix, self._name))

    @property
    def expression(self):
        return str(self._expression)

    @property
    def value(self):
        return self._param.value

    @property
    def units(self):
        return self._units

    def create(self):
        ui.messageBox('Name: {}\nExpression: {}'.format(self.name, self.expression))
        return set_value(self.name, self.expression, self.units)
