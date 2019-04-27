import traceback

from adsk.core import Point3D
from adsk.fusion import DimensionOrientations
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType
from adsk.fusion import SketchPoint

from ...util import axis_dir
from ...util import uimessage

from ..parameters import Parameters
from .rectangle import Rectangle

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
HorizontalDimension = DimensionOrientations.HorizontalDimensionOrientation
VerticalDimension = DimensionOrientations.VerticalDimensionOrientation


class FingerSketch:

    @classmethod
    def create(cls, fingertype, face, params=None, ui=None):
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == fingertype]
        return (sc[0](face, params)
                if len(sc) > 0
                else FingerSketch(face, params, ui))

    def __init__(self, face, tab_params, ui=None):
        self.__sketch = face.parent.sketches.add(face.bface)

        self.__tab_params = tab_params
        self._face = face
        self.face = self._face
        self._ui = ui

        profile = self.__sketch.profiles.item(0)
        self._max_point = profile.boundingBox.maxPoint
        self._min_point = profile.boundingBox.minPoint

        self.rectangle = Rectangle(self.__sketch,
                                   self.lines)
        self.bottom_dir = self.rectangle.bottom_dir
        self.left_dir = self.rectangle.left_dir

        if tab_params.parametric:
            self.parameters = Parameters(self, face.name, self.vertical,
                                         tab_params,
                                         axis_dir(self.__sketch.xDirection),
                                         axis_dir(self.__sketch.yDirection))
        else:
            self.parameters = None

        self.name = '{} {}-Axis'.format(self.face.name,
                                        (axis_dir(self.__sketch.yDirection)
                                         if self.vertical else
                                         axis_dir(self.__sketch.xDirection)
                                         ).upper())
        self.__sketch.name = '{} Finger Sketch'.format(self.name)

    @property
    def direction(self):
        return self.rectangle.direction

    @property
    def params(self):
        return self.__tab_params

    @property
    def curves(self):
        return self.__sketch.sketchCurves

    @property
    def dimensions(self):
        return self.__sketch.sketchDimensions

    @property
    def geometricConstraints(self):
        return self.__sketch.geometricConstraints

    @property
    def length(self):
        return max(self.x_length, self.y_length)

    @property
    def lines(self):
        return self.curves.sketchLines

    @property
    def points(self):
        return self.__sketch.sketchPoints

    @property
    def profiles(self):
        def maxpoint_x(profile):
            return profile.boundingBox.maxPoint.x

        def maxpoint_y(profile):
            return profile.boundingBox.maxPoint.y

        def minpoint_x(profile):
            return profile.boundingBox.minPoint.x

        def minpoint_y(profile):
            return profile.boundingBox.minPoint.y

        profiles = [self.__sketch.profiles.item(j)
                    for j in range(self.__sketch.profiles.count)]

        if self.vertical:
            if self.rectangle.left_dir == -1:
                profiles.sort(key=maxpoint_x)
                profiles.sort(key=maxpoint_y)
            else:
                profiles.sort(key=minpoint_x)
                profiles.sort(key=minpoint_y)
        else:
            if self.rectangle.bottom_dir == -1:
                profiles.sort(key=maxpoint_y)
                profiles.sort(key=maxpoint_x)
            else:
                profiles.sort(key=minpoint_y)
                profiles.sort(key=minpoint_x)

        return profiles

    @property
    def is_visible(self):
        return self.__sketch.isVisible

    @is_visible.setter
    def is_visible(self, val):
        self.__sketch.isVisible = val

    @property
    def vertical(self):
        return self.y_length > self.x_length

    @property
    def width(self):
        return min(self.x_length, self.y_length)

    @property
    def x_length(self):
        start = self._min_point.x
        end = self._max_point.x
        return end - start

    @property
    def y_length(self):
        start = self._min_point.y
        end = self._max_point.y
        return end - start

    def draw_finger(self):
        pass

    __draw_finger = draw_finger

    def _draw_rectangle(self, fp, sp):
        try:
            return Rectangle.draw(self.__sketch, fp, sp)
        except:
            uimessage(traceback.format_exc())

    def _next_point(self, point, width, backwards=False):
        if self.rectangle.is_vertical:
            xwidth = self.rectangle.width
            ywidth = width
        else:
            ywidth = self.rectangle.width
            xwidth = width

        return Point3D.create(point.x + xwidth,
                              point.y + ywidth,
                              point.z)

    def offset(self, point, offset=0):
        if type(point) is SketchPoint:
            o = point.geometry
        else:
            o = point

        if self.rectangle.is_vertical:
            o.y += offset
        else:
            o.x += offset

        return o

    @property
    def reference_line(self):
        if self.rectangle.is_vertical:
            return self.rectangle.left
        else:
            return self.rectangle.top

    @property
    def reference_points(self):
        if self.rectangle.is_vertical:
            return (self.rectangle.bottom_right.worldGeometry,
                    self.rectangle.top_right.worldGeometry)
        else:
            return (self.rectangle.top_right.worldGeometry,
                    self.rectangle.top_left.worldGeometry)

    @property
    def reference_plane(self):
        return self.__sketch.referencePlane
