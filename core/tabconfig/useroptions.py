import math

from collections import namedtuple

from adsk.core import ValueInput as vi

from ...util import distanceInputId
from ...util import dualEdgeSelectId
from ...util import fingerTypeId
from ...util import lengthInputId
from ...util import marginInputId
from ...util import mtlThickInputId
from ...util import parametricInputId
from ...util import selectedFaceInputId
from ...util import startWithTabInputId
from ...util import tabWidthInputId
from ...util import automaticWidthId
from ...util import errorMsgInputId

from ..base import Base
from ..fusion import Face
from ..fusion  import Body

class ParameterCreationError(Exception):
    pass

class UserOption(Base):

    @classmethod
    def frominput(cls, name, input_, units='cm', comment='', save=False):
        return cls(name, units=units, comment=comment, input_=input_, save=save)

    @classmethod
    def fromproperty(cls, parent):
        return cls(parent=parent)

    def __init__(self, name='', input_=None, value=0, expression='', parent=None, save=False, comment='', units='cm'):
        self.parent = self.init_input(name, input_) if input_ else parent
        self.__units = units
        self.__comment = comment
        self.__name = name
        self.__input = input_
        self.__value = value
        self.__expression = expression

        if save:
            self.save(units, comment)

    def init_input(self, name, input_):
        """ Return the parameter defined either by the input expression,
            a previously created parameter, or a newly created parameter.
            """
        param = self.design_parameters.itemByName(name)
        if param:
            return param

        param = self.design_parameters.itemByName(input_.expression)
        if param:
            return param

    @property
    def expression(self):
        if self.parent:
            return self.parent.name
        elif self.__input:
            return self.__input.expression
        else:
            return self.__expression

    @property
    def value(self):
        if self.parent:
            return self.parent.value
        elif self.__input:
            return self.__input.value
        else:
            return self.__value

    @property
    def name(self):
        if self.__name:
            return self.__name
        elif self.__input:
            return self.__input.name
        else:
            return self.parent.name

    def save(self, units='cm', comment='', parameter=None, valcheck=None):
        check = valcheck if valcheck else lambda x: x

        try:
            in_comment = comment if comment else 'TabGen parameter'
            expression = vi.createByString(self.expression)
            if not parameter:
                return self.user_parameters.add(self.__name, expression, self.__input.unitType, in_comment)
            else:
                if not self.parent:
                    parameter.name = self.__name
                    parameter.unit = self.__input.unitType if self.__input else units
                    parameter.expression = check(self.value, self.expression)
                else:
                    parameter.name = self.__name
                    parameter.unit = self.parent.unit
                    parameter.expression = check(self.parent.value, self.parent.name)

                parameter.comment = in_comment
                return parameter
        except:
            raise ParameterCreationError('Parameter: {}'.format(self.__name))


class InvalidFingerTypeException(Exception):
    pass


class OptionCreator(Base):

    def __init__(self, prefix):
        self.prefix = prefix

    def frominput(self, name, input_, save=False):
        return UserOption.frominput('{}_{}'.format(self.prefix, name),
                                    input_, save=save)


class UserOptions(Base):

    finger_type = automaticWidthId

    @classmethod
    def create(cls, inputs):
        finger_type = inputs.itemById(fingerTypeId).selectedItem.name
        if not finger_type:
            raise InvalidFingerTypeException

        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == finger_type]
        return (sc[0](inputs)
                if len(sc) > 0
                else cls(inputs))

    def __init__(self, inputs):
        super().__init__()

        self.face = Face(inputs.itemById(selectedFaceInputId).selection(0).entity)
        self.body = self.face.body

        second_edge = inputs.itemById(dualEdgeSelectId)
        self.edge = second_edge.selection(0).entity if second_edge.selectionCount > 0 else None
        self.parametric = inputs.itemById(parametricInputId).value
        self.start_with_tab = inputs.itemById(startWithTabInputId).value

        option = OptionCreator(self.face.alias)

        self.default_width = option.frominput('default_width', inputs.itemById(tabWidthInputId), save=True)
        self.margin = option.frominput('edge_margin', inputs.itemById(marginInputId), save=True)

        self.depth = option.frominput('depth', inputs.itemById(mtlThickInputId))
        self.distance = option.frominput('secondary_distance',
                                         inputs.itemById(distanceInputId))
        self.length = option.frominput('edge_length', inputs.itemById(lengthInputId))

    def add_option(self, name, value, expression, comment=None, save=False):
        option = option(name=name, value=value, expression=expression, comment=comment, save=save)
        setattr(self, name, option)

    # def custom_properties(self):
    #     self.tab_width = self.create_property('tab_width',
    #                                           self.length.value / self.default_fingers.value,
    #                                           '{0}_length / {0}_default_fingers')
    #     self.tab_width.add_parents([self.length, self.default_fingers])

    #     if self.start_with_tab:
    #         self.notch_length = self.create_property('notch_length',
    #                                                  (self.default_fingers.value - 3)*self.tab_width.value,
    #                                                  '-(({0}_default_fingers - 3) * {0}_tab_width)')
    #         self.notch_length.add_parents([self.default_fingers, self.tab_width])

    #         self.notches = self.create_property('notches',
    #                                             math.floor(self.default_fingers.value/2),
    #                                             'floor({0}_default_fingers/2)',
    #                                             units='')
    #         self.notches.add_parent(self.default_fingers)
    #     else:
    #         self.notch_length = self.create_property('notch_length',
    #                                                  (self.default_fingers.value - 1)*self.tab_width.value,
    #                                                  '-(({0}_default_fingers - 1) * {0}_tab_width)')
    #         self.notch_length.add_parents([self.default_fingers, self.tab_width])

    #         self.notches = self.create_property('notches',
    #                                             math.ceil(self.default_fingers.value/2),
    #                                             'ceil({0}_default_fingers/2)',
    #                                             units='')
    #         self.notches.add_parent(self.default_fingers)

    #     self.offset = self.create_property('offset',
    #                                        self.tab_width.value + self.margin.value,
    #                                        '({0}_length - {0}_notch_length)/2 + {0}_margin')
    #     self.offset.add_parents([self.length, self.margin, self.notch_length])

    # def default_properties(self):
    #     self.default_width = self.input_property(tabWidthInputId, 'default_width')
    #     self.default_depth = self.input_property(mtlThickInputId, 'default_depth', permanent=False)
    #     self.distance = self.input_property(distanceInputId, 'distance')
    #     self.default_length = self.input_property(lengthInputId, 'default_length', permanent=False)
    #     self.margin = self.input_property(marginInputId, 'margin')

    #     self.depth = self.create_property('depth',
    #                                       -abs(self.default_depth.value),
    #                                       '-abs({0})'.format(self.default_depth.expression))

    #     self.length = self.create_property('length',
    #                            self.default_length.value - abs(self.margin.value)*2,
    #                            '{0} - abs({1}) * 2'.format(self.default_length.expression,
    #                                                        '{0}_{1}'.format('{0}',
    #                                                                         self.margin.name)))
    #     self.length.add_parents([self.margin])

    #     self.default_fingers = self.create_property('default_fingers',
    #                                                 max(3, (math.ceil(math.floor(self.length.value / self.default_width.value)/2)*2)-1),
    #                                                 'max(3; (ceil(floor({0}_length / {0}_default_width)/2)*2)-1)',
    #                                                 units='')
    #     self.default_fingers.add_parents([self.length, self.default_width])

    #     self.second_distance = self.create_property('second_distance',
    #                                     self.distance.value - abs(self.depth.value),
    #                                     '{0} - abs({1})'.format('{0}_{1}'.format('{0}', self.distance.name),
    #                                                             '{0}_{1}'.format('{0}', self.depth.name)),
    #                                     test=lambda x: x>0)
    #     self.second_distance.add_parents([self.distance, self.depth])

    # __default_properties = default_properties
    # __custom_properties = custom_properties

    # def input_property(self, inputid, name, permanent=True, units='cm', comment=''):
    #     cmd_input = self.inputs.itemById(inputid)
    #     prop = Property.create_from_input(cmd_input, name, permanent, units, comment)
    #     self.properties.append(prop)
    #     return prop

    # def create_property(self, name, value, expression, units='cm', comment='', test=None):
    #     exp = expression.format(self.prefix)
    #     prop = Property.create(name, value, exp, units=units, comment=comment, test=test)
    #     self.properties.append(prop)
    #     return prop

    # def save_properties(self, prefix):
    #     for prop in self.properties:
    #         prop.save(prefix)
