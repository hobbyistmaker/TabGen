from collections import namedtuple

Property = namedtuple('Property', ['name', 'value', 'expression', 'unit', 'comment'])


def create_property(app, prefix, name, value,
                    expression=None, unit='cm', comment=''):
    expr = expression if expression else str(value)
    design = app.activeProduct
    parameters = design.allParameters

    param = parameters.itemByName(expression)
    if param:
        return param

    return Property('{}_{}'.format(prefix, name),
                    value,
                    expr,
                    unit,
                    comment)
