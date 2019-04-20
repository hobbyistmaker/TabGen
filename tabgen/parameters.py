from .parameter import Parameter

from ..util import automaticWidthId
from ..util import clean_param
from ..util import userDefinedWidthId


class Parameters:

    def __init__(self, parent, name, vertical, tab_params, xdir, ydir):
        dirname = ydir if vertical else xdir
        self.name = clean_param(name)
        self.prefix = '{}_{}'.format(self.name,
                                     dirname)

        self._xlength = Parameter(name,
                                  '{}_length'.format(xdir),
                                  parent.x_length)
        self._ylength = Parameter(name,
                                  '{}_length'.format(ydir),
                                  parent.y_length)
        self._dfingerw = Parameter(self.prefix,
                                   'dfingerw',
                                   '{}_dfingerw'.format(self.name))

        self.create_params(tab_params)

    def create_params(self, tab_params):
        funcs = {
            automaticWidthId: self.create_auto_params,
            userDefinedWidthId: self.create_defined_params
        }
        func = funcs[tab_params.finger_type]
        func(tab_params)

    def create_auto_params(self, tab_params):
        self.fingers = Parameter(self.prefix,
                                 'fingers',
                                 'max(3; (ceil(floor({0}_length/{0}_dfingerw)/2)*2)-1)',
                                 units='')
        self.fingerw = Parameter(self.prefix,
                                 'fingerw',
                                 '{0}_length / {0}_fingers')
        self.foffset = Parameter(self.prefix,
                                 'foffset',
                                 '{0}_fingerw')
        self.notches = Parameter(self.prefix,
                                 'notches',
                                 'floor({0}_fingers/2)',
                                 units='')
        self.extrude_count = Parameter(self.prefix,
                                       'extrude_count',
                                       '{0}_notches',
                                       units='')
        self.fdistance = Parameter(self.prefix,
                                   'fdistance',
                                   '({0}_fingers - 3)*{0}_fingerw')

    def create_defined_params(self, tab_params):
        self.fingers = Parameter(self.prefix,
                                 'fingers',
                                 'floor({0}_length / {0}_dfingerw)',
                                 units='')
        self.fingerw = Parameter(self.prefix,
                                 'fingerw',
                                 '{0}_dfingerw')
        self.notches = Parameter(self.prefix,
                                 'notches',
                                 'floor({0}_length / (2 * {0}_fingerw))',
                                 units='')
        self.notch_length = Parameter(self.prefix,
                                      'notch_length',
                                      '2 * {0}_fingerw * {0}_notches')
        self.foffset = Parameter(self.prefix,
                                 'foffset',
                                 '({0}_length - {0}_notch_length + {0}_fingerw)/2')
        self.extrude_count = Parameter(self.prefix,
                                       'extrude_count',
                                       '{0}_notches - 1',
                                       units='')
        self.fdistance = Parameter(self.prefix,
                                   'fdistance',
                                   '{0}_length - {0}_foffset*2 - {0}_fingerw')

    @property
    def xlength(self):
        return self._xlength

    @property
    def ylength(self):
        return self._ylength
