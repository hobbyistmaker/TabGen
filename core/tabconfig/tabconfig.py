import math

from collections import namedtuple

from ..base import Base
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
from. ..util import automaticWidthId

Property = namedtuple('Property', ['name', 'value', 'expression'])


class TabConfig(Base):

    finger_type = automaticWidthId

    @classmethod
    def create(cls, inputs):
        finger_type = inputs.itemById(fingerTypeId).selectedItem.name
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == finger_type]
        return (sc[0](inputs)
                if len(sc) > 0
                else cls(inputs))

    def __init__(self, inputs):
        super().__init__()

        self.inputs = inputs
        self.__default_properties()

    def default_properties(self):
        self.length = Property('length',
                               self.default_length.value - abs(self.margin.value)*2,
                               '{0}_length - abs({0}_margin) * 2')
        self.default_fingers = Property('default_fingers',
                                        max(3, (math.ceil(math.floor(self.length.value / self.default_width.value)/2)*2)-1),
                                        'max(3, (ceil(floor({0}_length / {0}_default_width)/2)*2)-1)')
        self.tab_width = Property('tab_width',
                                  self.length.value / self.default_fingers.value,
                                  '{0}_length / {0}_default_fingers')
        self.second_distance = Property('second_distance',
                                        self.distance.value - abs(self.depth.value),
                                        '{0}_distance - abs({0}_depth)')

        if self.start_with_tab:
            self.notch_length = Property('notch_length',
                                         (self.default_fingers.value - 3)*self.tab_width.value,
                                         '({0}_default_fingers - 3) * {0}_tab_width')
            self.notches = Property('notches',
                                    math.floor(self.default_fingers.value/2),
                                    'floor({0}_default_fingers/2)')
        else:
            self.notch_length = Property('notch_length',
                                         (self.default_fingers.value - 1)*self.tab_width.value,
                                         '({0}_default_fingers - 1) * {0}_tab_width')
            self.notches = Property('notches',
                                    math.ceil(self.default_fingers.value/2),
                                    'ceil({0}_default_fingers/2)')

        self.offset = Property('offset',
                               self.tab_width.value + self.margin.value,
                               '{0}_length + {0}_margin')

    __default_properties = default_properties

    @property
    def default_width(self):
        return self.inputs.itemById(tabWidthInputId)

    @property
    def depth(self):
        return self.inputs.itemById(mtlThickInputId)

    @property
    def distance(self):
        return self.inputs.itemById(distanceInputId)

    @property
    def edge(self):
        return self.inputs.itemById(dualEdgeSelectId).selection(0).entity

    @property
    def face(self):
        return self.inputs.itemById(selectedFaceInputId).selection(0).entity

    @property
    def default_length(self):
        return self.inputs.itemById(lengthInputId)

    @property
    def margin(self):
        return self.inputs.itemById(marginInputId)

    @property
    def parametric(self):
        return self.inputs.itemById(parametricInputId).value

    @property
    def start_with_tab(self):
        return self.inputs.itemById(startWithTabInputId).value
