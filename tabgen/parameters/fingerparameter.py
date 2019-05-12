from adsk.core import Application
from adsk.fusion import Design
from adsk.core import ValueInput

createByReal = ValueInput.createByReal
createByString = ValueInput.createByString

app = Application.get()
ui = app.userInterface


COMMENTSTR = 'Auto-generated parameter'


class FingerParameter:

    def __init__(self, name, expression, value,
                 comment='', units='cm', save=False):
        self._des = Design.cast(app.activeProduct)
        self._user_params = self._des.userParameters

        self._name = self.__clean_name(name)
        self._expression = expression
        self._value = value
        self._comment = comment if comment else COMMENTSTR
        self._units = units
        self._copies = []

        self._entity = None
        if save:
            self.save()

    def __clean_name(self, param):
        for ch in [' ', '-', '(', ')']:
            if ch in param:
                param = param.replace(ch, '_')
        return param.lower()

    @property
    def name(self):
        return self._name

    @property
    def expression(self):
        if self._expression:
            return self._expression
        return '{} {}'.format(self._value, self._units)

    @property
    def value(self):
        return self._value

    @property
    def comment(self):
        return self._comment

    @property
    def units(self):
        return self._units

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, value):
        self._entity = value

    @property
    def user_params(self):
        return self._user_params

    def copy(self, value):
        self._copies.append(value)

    def save(self, favorite=False, temp=False):
        input_value = str(self.expression)
        if self.entity:
            self.entity.name = self.name
            if temp is False:
                self.entity.expression = self.expression
            else:
                self.entity.value = self.value
            self.entity.comment = self.comment
            self.entity.units = self.units
            retval = self.entity
        else:
            param = self.user_params.itemByName(self.name)

            if not param:
                param = self.user_params.add(self.name,
                                              createByString(input_value),
                                              self.units,
                                              self.comment)
            retval = param

        for copy in self._copies:
            if temp is False:
                copy.expression = self.name
            else:
                copy.value = self.value
            copy.comment = self.comment
            copy.units = self.units

        retval.isFavorite = True
        return retval

