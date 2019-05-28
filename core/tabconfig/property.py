import traceback

from collections import namedtuple

from adsk.core import ValueInput as vi

from ..base import Base


Assignment = namedtuple('Assignment', ['name', 'parameter'])


class Property(Base):

    def __init__(self,
                 parameter=None,
                 cmd_input=None,
                 name='',
                 value=0,
                 expression='',
                 parents=None,
                 permanent=True,
                 units='cm',
                 comment='',
                 test=None):
        self.parameter = parameter
        self.cmd_input = cmd_input
        self.name = name
        self.alias = name
        self.__value = value
        self.__expression = str(expression) if expression else str(value)
        self.parents = [] if parents is None else parents
        self.permanent = permanent
        self.units = units
        self.comment = comment
        self.assigned = None
        self.saved = False
        self.test = test

    @classmethod
    def create_from_input(cls, cmd_input, name, permanent=True, units='cm', comment=''):
        param = cls.design_parameters.itemByName(cmd_input.expression)
        if param:
            return Property.create_from_parameter(param, alias=name)
        return InputProperty(cmd_input, name, permanent, units, comment)

    @classmethod
    def create_from_parameter(cls, parameter, alias=''):
        return ParameterProperty(parameter, alias=alias, permanent=False)

    @classmethod
    def create(cls, name, value, expression, permanent=True, units='cm', comment='', test=None):
        return NamedProperty(name, value, expression, permanent, units, comment, test=test)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def expression(self):
        return self.__expression

    @expression.setter
    def expression(self, value):
        self.__expression = value

    def add_parent(self, parent):
        self.parents.append(parent)

    def add_parents(self, parents):
        self.parents += parents

    def assign(self, name, param):
        self.assigned = Assignment(name, param)

    def save(self, prefix):
        if (self.test and self.test(self.value) is True) or self.test is None:
            for parent in self.parents:
                parent.save(prefix)

            try:
                expression = self.expression.format(prefix)
                if self.saved is False:
                    if self.assigned is not None:
                        param = self.assigned.parameter
                        # self.msg('Saving assigned parameter: {} to {}'.format(self.name, self.assigned.name))
                        param.name = '{0}_{1}'.format(prefix, self.assigned.name)
                        param.value = self.value
                        param.expression = expression
                        param.units = self.units
                        param.comment = self.comment
                        # self.msg('Saved assigned parameter: {}'.format(self.name))
                    elif self.permanent is True:
                        self.design.userParameters.add('{0}_{1}'.format(prefix, self.name),
                                                       vi.createByString(expression),
                                                       self.units,
                                                       self.comment)

                    self.__save_data(prefix)
                    self.saved = True
            except:
                self.msg('Error saving property {}: {}'.format('{0}_{1}'.format(prefix,
                                                                                self.name),
                                                               expression)
                )
                self.msg(traceback.format_exc())

    def save_data(self, prefix):
        pass

    __save_data = save_data


class InputProperty(Property):

    def __init__(self, cmd_input, name, permanent, units, comment):
        super().__init__(name=name, cmd_input=cmd_input, permanent=permanent)

    @property
    def value(self):
        return self.cmd_input.value

    @property
    def expression(self):
        return self.cmd_input.expression


class NamedProperty(Property):

    def __init__(self, name, value, expression='', permanent=True, units='cm', comment='', test=None):
        super().__init__(name=name, value=value, expression=expression,
                         permanent=permanent, units=units, comment=comment, test=test)

    def save_data(self, prefix):
        params = self.design.userParameters
        expression = self.expression.format(prefix)

        if self.permanent:
            params.add('{0}_{1}'.format(prefix, self.name),
                       vi.createByString(expression),
                       units,
                       comment)


class ParameterProperty(Property):

    def __init__(self, parameter, alias='', permanent=True):
        super().__init__(parameter=parameter, permanent=permanent)

        self.alias = alias
        self.references = []

    @property
    def name(self):
        return self.parameter.name

    @name.setter
    def name(self, value):
        self.parameter.name = value

    @property
    def value(self):
        return self.parameter.value

    @value.setter
    def value(self, value):
        self.parameter.value = value

    @property
    def expression(self):
        return self.parameter.expression

    @expression.setter
    def expression(self, value):
        self.parameter.expression = value

    def save(self, prefix):
        if self.assigned is not None:
            param = self.assigned.parameter
            param.name = '{0}_{1}'.format(prefix, self.assigned.name)
            param.expression = self.name
