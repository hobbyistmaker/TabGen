import traceback

from adsk.core import ObjectCollection as oc
from adsk.core import ValueInput as vi
from adsk.fusion import FeatureOperations as fo
from adsk.fusion import PatternDistanceType as pdt

from ...util import automaticWidthId

from ..base import Base
from ..operations import TimelineGroup
from ..tabconfig import TabConfig

from .property import Property


class Fingers(Base):

    finger_type = automaticWidthId

    @classmethod
    def create(cls, face, inputs):
        config = TabConfig.create(inputs)
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == config.finger_type]
        return (sc[0](face, config)
                if len(sc) > 0
                else cls(face, config))

    def __init__(self, face, config):
        super().__init__()

        self.face = face
        self.config = config
        self.name = self.clean_string(self.face.name)

        self.timeline = TimelineGroup('{} Finger Group'.format(self.name),
                                        self.__execute)

    def duplicate_notches(self, name, primary, secondary, features):
        try:
            conf = self.config
            patterns = self.face.patterns
            alias = self.clean_string(self.name)
            notches = conf.notches.value
            notch_length = conf.notch_length.value

            inputs = oc.create()
            inputs.add(features)

            pattern = patterns.createInput(inputs,
                                           primary,
                                           vi.createByReal(notches),
                                           vi.createByReal(notch_length),
                                           pdt.ExtentPatternDistanceType)

            if secondary is not None:
                parallel_distance = vi.createByReal(conf.second_distance.value)
                pattern.setDirectionTwo(secondary,
                                        vi.createByReal(2),
                                        parallel_distance)
                # in the future, make the number of cuts in the second
                # direction user definable for walls in the middle of the
                # body

            patterns.add(pattern)

            return pattern
        except:
            self.msg(traceback.format_exc())

    def execute(self):
        sketch = self.face.add_sketch()
        conf = self.config
        offset = conf.offset.value
        width = conf.tab_width.value

        try:
            ref_points = sketch.reference_points
            primary_axis = sketch.reference_line
            secondary = self.face.perpendicular_from_vertex(ref_points.second)

            swt = conf.start_with_tab
            stp = sketch.start_point

            fsp = stp if not swt else sketch.offset_point(stp,
                                                          offset,
                                                          same_line=True)

            sketch.draw_rectangle(fsp, width)
        except:
            self.msg(traceback.format_exc())

        self.finger = self.extrude('{} Finger'.format(self.name),
                                   conf.depth.expression,
                                   sketch.profiles[0])
        self.pattern = self.duplicate_notches('{} Finger'.format(self.name),
                                              primary_axis,
                                              secondary.edge,
                                              self.finger)
        self.save_parameters()

    __execute = execute

    def extrude(self, name, depth, profiles):
        try:
            value = vi.createByString('-abs({})'.format(depth))

            input = self.face.extrudes.createInput(profiles,
                                                   fo.CutFeatureOperation)
            input.setDistanceExtent(False, value)
            input.participantBodies = [self.body.brepbody]

            finger = self.face.extrudes.add(input)
            finger.name = '{} Extrude'.format(name)

            return finger
        except:
            self.msg(traceback.format_exc())

    def save_parameters(self):
        pass

    __save_parameters = save_parameters

    @property
    def body(self):
        return self.face.body
