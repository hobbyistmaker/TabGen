from .createproperty import create_property

def input_property(app, prefix):
    def prop(name, source, comment):
        return create_property(app,
                               prefix,
                               name,
                               getattr(source, 'value'),
                               getattr(source, 'expression'),
                               getattr(source, 'unitType'),
                               'TabGen: {}'.format(comment))
    return prop
