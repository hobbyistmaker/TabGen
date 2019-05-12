from adsk.core import Application
from adsk.fusion import Design
from adsk.core import ValueInput

app = Application.get()
ui = app.userInterface

createByReal = ValueInput.createByReal
createByString = ValueInput.createByString


def clean_param(param):
    return param.replace(' ', '_').replace('(', '').replace(')', '').lower()


def set_value(name,
              value,
              user_params,
              units='cm',
              favorite=False,
              comment=''):
    inputValue = str(value)
    itemParam = user_params.add(name,
                                createByString(inputValue),
                                units,
                                comment if comment
                                else 'Auto-generated parameter')
    itemParam.isFavorite = favorite
    return itemParam


class Parameter:

    def __init__(self, prefix, name,
                 expression, units='cm',
                 favorite=False,
                 comment=''):
        des = Design.cast(app.activeProduct)

        self.user_params = des.userParameters

        self.prefix = prefix if isinstance(prefix, str) else str(prefix)
        self._expression = expression.format(prefix) if isinstance(expression, str) else expression
        self._name = name if isinstance(name, str) else str(name)
        self._units = units if isinstance(units, str) else ''
        self._comment = comment

        self._favorite = favorite

        self._param = self.user_params.itemByName(self.name)
        if not (self._param):
            self._param = self.save()

    @property
    def comment(self):
        return self._comment

    @property
    def comment(self):
        return self._comment

    @property
    def name(self):
        return clean_param('{0}_{1}'.format(self.prefix, self._name))

    @property
    def expression(self):
        return str(self._expression)

    @property
    def favorite(self):
        return self._favorite

    @property
    def value(self):
        return self._param.value

    @property
    def units(self):
        return self._units

    def save(self):
        return set_value(self.name, self.expression, self.user_params,
                         self.units, self.favorite, self.comment)
