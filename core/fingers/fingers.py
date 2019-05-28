import math
import traceback

from adsk.core import ObjectCollection as oc
from adsk.core import ValueInput as vi
from adsk.fusion import FeatureOperations as fo
from adsk.fusion import PatternDistanceType as pdt

from ...util import automaticWidthId

from ..base import Base
from ..operations import TimelineGroup
from ..tabconfig import UserOptions

from .property import Property


class Fingers(Base):

    finger_type = automaticWidthId

    @classmethod
    def create(cls, options):
        face = options.face

        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == options.finger_type]
        return (sc[0](face, options)
                if len(sc) > 0
                else cls(face, options))

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
            notches = self.notches
            notch_distance = self.notch_distance if not self.second_distance else -self.notch_distance
            edge = secondary.edge if self.second_distance > 0 else None

            inputs = oc.create()
            inputs.add(features)

            pattern = patterns.createInput(inputs,
                                           primary,
                                           vi.createByReal(notches),
                                           vi.createByReal(notch_distance),
                                           pdt.ExtentPatternDistanceType)

            parallel_distance = vi.createByReal(self.second_distance)
            pattern.setDirectionTwo(edge,
                                    vi.createByReal(2),
                                    parallel_distance)
            # in the future, make the number of cuts in the second
            # direction user definable for walls in the middle of the
            # body

            feature = patterns.add(pattern)

            return feature
        except:
            self.msg(traceback.format_exc())

    def execute(self):
        sketch = self.face.add_sketch()
        self.face.mark_complete()
        conf = self.config

        self.add_options(conf)

        offset = self.offset
        width = self.tab_width

        try:
            ref_points = sketch.reference_points
            primary_axis = sketch.reference_line
            secondary = self.face.perpendicular_from_vertex(ref_points.second)

            swt = conf.start_with_tab
            stp = sketch.start_point

            fsp = stp if not swt else sketch.offset_point(stp,
                                                          offset,
                                                          width=0)

            self.margin_line = sketch.draw_margin(fsp)

            finger_sketch = sketch.draw_rectangle(fsp, width, constrain=True)
        except:
            self.msg(traceback.format_exc())

        self.finger = self.extrude('{} Finger'.format(self.name),
                                   conf.depth.expression,
                                   sketch.profiles[0])

        self.pattern = self.duplicate_notches('{} Finger'.format(self.name),
                                              primary_axis,
                                              secondary,
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
        def check_negative(value, expression):
            if value > 0:
                return '-({})'.format(expression)
            else:
                return expression

        def check_positive(value, expression):
            if value < 0:
                return 'abs({})'.format(expression)
            else:
                return expression

        self.config.depth.save(parameter=self.finger.extentOne.distance, valcheck=check_negative)


    __save_parameters = save_parameters

    @property
    def body(self):
        return self.face.body

    @property
    def adjusted_length(self):
        return self.config.length.value - self.config.margin.value * 2

    @property
    def fingers(self):
        return max(3, (math.ceil(math.floor(self.adjusted_length / self.config.default_width.value)/2)*2)-1)

    @property
    def notch_distance(self):
        return (self.fingers - (3 if self.config.start_with_tab else 1)) * self.tab_width

    @property
    def notches(self):
        return math.floor(self.fingers/2) if self.config.start_with_tab else math.ceil(self.fingers/2)

    @property
    def offset(self):
        return (self.config.length.value - (self.adjusted_length - self.tab_width * (2 if self.config.start_with_tab else 0)))/2

    @property
    def second_distance(self):
        distance = self.config.distance.value
        depth = self.config.depth.value
        return (distance - depth) if distance > depth else 0

    @property
    def tab_width(self):
        return self.adjusted_length / self.fingers

    def add_options(self, conf):
        adjusted_length = '{} - {} * 2'.format(conf.length.name, conf.margin.name)
        fingers = 'max(3; (ceil(floor({} / {})/2)*2)-1)'.format(adjusted_length, conf.default_width.name)
        notches = ('floor({}/2)' if conf.start_with_tab else 'ceil({}/2)').format(fingers)
        notch_distance = '({}*2){}'.format(notches, '')
