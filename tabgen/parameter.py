from ..util import check_param


class Parameter:

    def __init__(self, prefix, name, expression, units='cm'):
        self.prefix = prefix if isinstance(prefix, str) else str(prefix)
        self._expression = expression.format(prefix) if isinstance(expression, str) else expression
        self._name = name if isinstance(name, str) else str(name)
        self._units = units if isinstance(units, str) else ''

        self.create()

    @property
    def name(self):
        return '{0}_{1}'.format(self.prefix, self._name)

    @property
    def expression(self):
        return str(self._expression)

    @property
    def units(self):
        return self._units

    def create(self):
        check_param(self.name, self.expression, units=self.units)
