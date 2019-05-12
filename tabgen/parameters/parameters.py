from adsk.core import Application

from .parameter import Parameter

from ..util import automaticWidthId
from ..util import userDefinedWidthId


app = Application.get()
ui = app.userInterface


def clean_param(param):
    return param.replace(' ', '_').replace('(', '').replace(')', '').lower()


class Parameters:

    @classmethod
    def create(cls, parent, config, directions):
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == config.finger_type]
        return (sc[0](parent, config, directions)
                if len(sc) > 0
                else Parameters(parent, config, directions))

    def __init__(self, parent, config, directions):
        self._parent = parent
        self._config = config
        self._vertical = parent.vertical

        dirname = direction[1] parent.vertical else directions[0]
        self.face_num = parent.face.face_count
        self._clean_name = clean_param(parent.name)
        self.prefix = '{0}_{1}{2}'.format(self._clean_name,
                                          dirname,
                                          self.face_num)

        self.x, self.y, self.z = (False, False, False)

        if (xdir == 'x' or ydir == 'x'):
            self.x = True
        if (xdir == 'y' or ydir == 'y'):
            self.y = True
        if (xdir == 'z' or ydir == 'z'):
            self.z = True

        self._pdfingerw = Parameter(parent.face.name,
                                    'dfingerw',
                                    config.default_width.expression,
                                    favorite=True,
                                    comment='Auto: change to desired target width for fingers')
        if parent.vertical:
            if config.parametric:
                yparam = config.length.expression
            else:
                yparam = abs(round(parent.y_length, 5))

            self._ylength = Parameter(parent.name,
                                      '{}{}_length'.format(ydir, self.face_num),
                                      yparam,
                                      favorite=True,
                                      comment='Auto: change to proper user parameter length')
        else:
            if config.parametric:
                xparam = config.length.expression
            else:
                xparam = abs(round(parent.x_length, 5))
            self._xlength = Parameter(parent.name,
                                      '{}{}_length'.format(xdir, self.face_num),
                                      xparam,
                                      favorite=True,
                                      comment='Auto: change to proper user parameter length')

        self._dfingerw = Parameter(self.prefix,
                                   'dfingerw',
                                   '{}_dfingerw'.format(self._clean_name))
        self._fingerd = Parameter(self.prefix,
                                  'fingerd',
                                  'abs({})'.format(config.depth.expression),
                                  favorite=True,
                                  comment='Auto: change to proper depth of fingers')

        if config.parametric:
            fingerd = 'abs({})'.format(config.depth.expression)
            disttwo = '{} - {}'.format(config.distance_two.expression,
                                       self.fingerd.name)
            margin = 'abs({})'.format(config.margin.expression)
        else:
            fingerd = abs(config.depth.value)
            disttwo = config.distance_two.value - fingerd
            margin = abs(config.margin.value)

        self.distance_two = Parameter(self._clean_name,
                                      '{}{}_distance2'.format(self._alternate_axis, self.face_num),
                                      disttwo
                                      )
        self._fingerd = Parameter(self.prefix,
                                  'fingerd',
                                  fingerd,
                                  favorite=True,
                                  comment='Auto: change to proper depth of fingers')
        self._margin = Parameter(self.prefix,
                                 'margin',
                                 margin,
                                 favorite=True,
                                 comment='Auto: change to margin offset from edge')
        self.fingers = Parameter(self.prefix,
                                 'fingers',
                                 'max(3; (ceil(floor({0}_length/{0}_dfingerw)/2)*2)-1)',
                                 units='',
                                 comment='Auto: calculates the total number of fingers for axis')

        self.create_config(config)

    def create_config(self, config):
        funcs = {
            automaticWidthId: self.create_auto_config,
            userDefinedWidthId: self.create_defined_config
        }
        func = funcs[config.finger_type]
        func(config)

    def create_auto_config(self, config):
        self.fingerw = Parameter(self.prefix,
                                 'fingerw',
                                 '{0}_length / {0}_fingers',
                                 comment='Auto: determines width of fingers to fit on axis')
        self.foffset = Parameter(self.prefix,
                                 'foffset',
                                 '{0}_fingerw + {0}_margin',
                                 comment='Auto: sets the offset from the edge for the first notch')
        self.notches = Parameter(self.prefix,
                                 'notches',
                                 'floor({0}_fingers/2)',
                                 units='',
                                 comment='Auto: determines the number of notches to cut along the axis')
        self.extrude_count = Parameter(self.prefix,
                                       'extrude_count',
                                       '{0}_notches' if config.start_with_tab else '{0}_fingers - {0}_notches',
                                       units='',
                                       comment='Auto: number of notches to extrude')
        self.fdistance = Parameter(self.prefix,
                                   'fdistance',
                                   '-({})'.format('({0}_fingers - 3)*{0}_fingerw' if config.start_with_tab else '({0}_fingers - 1)*{0}_fingerw'),
                                   comment='Auto: distance over which notches should be placed')

    def create_defined_config(self, config):
        if config.start_with_tab is True:
            tab_count = Parameter(self.prefix,
                                  'tab_count',
                                  'ceil({}/2)'.format(self.fingers.name),
                                  comment='Auto: number of tabs across the face',
                                  units='')
            notch_count = Parameter(self.prefix,
                                    'notch_count',
                                    '{0} - 1'.format(tab_count.name),
                                    units='')
            tab_length = Parameter(self.prefix,
                                   'pattern_length',
                                   '{0} * {1} - {0}*2'.format(self.dfingerw.name, self.fingers.name))
        else:
            notch_count = Parameter(self.prefix,
                                    'notch_count',
                                    'ceil({0}/2) - 2'.format(self.fingers.name),
                                    units='')
            tab_count = Parameter(self.prefix,
                                  'tab_count',
                                  '{0} - 1'.format(notch_count.name),
                                  units='')
            tab_length = Parameter(self.prefix,
                                   'pattern_length',
                                   '{0} * {1}'.format(self.dfingerw.name, self.fingers.name))

        self.fingerw = Parameter(self.prefix,
                                 'fingerw',
                                 '{0}_dfingerw')
        self.notches = notch_count
        self.notch_length = tab_length
        self.foffset = Parameter(self.prefix,
                                 'foffset',
                                 '({0} - {1} + {2})/2'.format(self.length.name,
                                                              tab_length.name,
                                                              self.dfingerw.name))
        self.fdistance = tab_length

    @property
    def _alternate_axis(self):
        if not self.x:
            return 'x'
        if not self.y:
            return 'y'
        if not self.z:
            return 'z'

    @property
    def margin(self):
        return self._margin

    @property
    def name(self):
        return self._parent.name

    @property
    def xlength(self):
        return self._xlength

    @property
    def ylength(self):
        return self._ylength

    @property
    def fingerd(self):
        return self._fingerd

    @property
    def dfingerw(self):
        return self._dfingerw

    @property
    def length(self):
        if self._vertical:
            return self._ylength
        else:
            return self._xlength
