import logging
import traceback

from adsk.core import Application
from adsk.core import Point3D
from adsk.fusion import DimensionOrientations
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType
from adsk.fusion import SketchPoint

from ...util import automaticWidthId
from ...util import axis_dir

from .rectangle import Rectangle

app = Application.get()
ui = app.userInterface

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
HorizontalDimension = DimensionOrientations.HorizontalDimensionOrientation
VerticalDimension = DimensionOrientations.VerticalDimensionOrientation

logger = logging.getLogger('fingersketch')


class FingerSketch:

    finger_type = automaticWidthId

    @classmethod
    def create(cls, manager, face, config):
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == config.finger_type]
        return (sc[0](manager, face, config)
                if len(sc) > 0
                else FingerSketch(manager, face, config))

    def __init__(self, manager, face, config):
        self.__config = config
        self.__face = face
        self.__face.sketch = self

        self.__sketch = face.parent.sketches.add(face.bface)

        profile = self.sketch.profiles.item(0)
        self.__max_point = profile.boundingBox.maxPoint
        self.__min_point = profile.boundingBox.minPoint

        self.__xdir = axis_dir(self.sketch.xDirection)
        self.__ydir = axis_dir(self.sketch.yDirection)

        self.__name = '{} {}-Axis'.format(face.name,
                                          (self.__ydir
                                           if self.vertical else
                                           self.__xdir
                                           ).upper())

        self.sketch.name = self.sketch_alias

        self.__rectangle = Rectangle(self.sketch,
                                     self.lines,
                                     construction=True)

        self.bottom_dir = self.rectangle.bottom_dir
        self.left_dir = self.rectangle.left_dir

    def profiles(self, rectangle, profiles):
        def maxpoint_x(profile):
            return profile.boundingBox.maxPoint.x

        def maxpoint_y(profile):
            return profile.boundingBox.maxPoint.y

        def minpoint_x(profile):
            return profile.boundingBox.minPoint.x

        def minpoint_y(profile):
            return profile.boundingBox.minPoint.y

        profiles = [profiles.item(j)
                    for j in range(profiles.count)]

        if self.vertical:
            if rectangle.left_dir == -1:
                profiles.sort(key=maxpoint_x)
                profiles.sort(key=maxpoint_y)
            else:
                profiles.sort(key=minpoint_x)
                profiles.sort(key=minpoint_y)
        else:
            if rectangle.bottom_dir == -1:
                profiles.sort(key=maxpoint_y)
                profiles.sort(key=maxpoint_x)
            else:
                profiles.sort(key=minpoint_y)
                profiles.sort(key=minpoint_x)

        return profiles

    def draw_fingers(self):
        width = self.config.default_width.value
        ofs = self.config.margin.value

        fsp = self.rectangle.bottom_left.geometry

        if self.config.start_with_tab is False:
            start_point = fsp
        else:
            start_point = self.offset(fsp, ofs)

        end_point = self._next_point(start_point, width)
        rectangle = self._draw_rectangle(start_point, end_point)

        self.set_finger_constraints(rectangle)

        self.is_visible = False
        return self.profiles

    def set_finger_constraints(self, rectangle):
        tabdim = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            rectangle.bottom_right,
            HorizontalDimension,
            Point3D.create(2, -1, 0))

        self.geometricConstraints.addCoincident(
            rectangle.top_right,
            self.rectangle.top.sketch_line)

        if self.config.start_with_tab is True:
            margindim = self.dimensions.addDistanceDimension(
                rectangle.bottom_left,
                self.rectangle.bottom_left,
                HorizontalDimension,
                Point3D.create(3, -1, 0))

            self.geometricConstraints.addCoincident(
                rectangle.bottom_left,
                self.rectangle.bottom.sketch_line)

        else:
            self.geometricConstraints.addCoincident(
                rectangle.bottom_left,
                self.rectangle.bottom_left)

    def _draw_margin(self, fp):
        start_point = self._margin_start(fp, self.config.margin.value)
        end_point = self._margin_end(start_point)
        marginline = self.lines.addByTwoPoints(start_point, end_point)
        marginline.isConstruction = True

        self.margindim = self.dimensions.addDistanceDimension(
            self.rectangle.bottom_left,
            marginline.startSketchPoint,
            HorizontalDimension,
            Point3D.create(2, -1, 0))
        self.geometricConstraints.addPerpendicular(self.rectangle.bottom.sketch_line,
                                                   marginline)

        return marginline

    def _draw_rectangle(self, fp, sp):
        try:
            return Rectangle.draw(self.__sketch, fp, sp)
        except:
            ui.messageBox(traceback.format_exc())

    def _next_point(self, point, width, backwards=False):
        if self.rectangle.is_vertical:
            xwidth = self.rectangle.width
            ywidth = width
        else:
            ywidth = self.rectangle.width
            xwidth = width

        xpoint = point.x + xwidth
        ypoint = point.y + ywidth

        return Point3D.create(xpoint, ypoint, point.z)

    def _margin_start(self, point, margin):
        if self.rectangle.is_vertical:
            xwidth = 0
            ywidth = margin
        else:
            ywidth = 0
            xwidth = margin

        xpoint = point.x + xwidth
        ypoint = point.y + ywidth
        return Point3D.create(xpoint, ypoint, point.z)

    def _margin_end(self, point):
        if self.rectangle.is_vertical:
            xwidth = self.rectangle.width
            ywidth = 0
        else:
            ywidth = self.rectangle.width
            xwidth = 0

        xpoint = point.x + xwidth
        ypoint = point.y + ywidth
        return Point3D.create(xpoint, ypoint, point.z)

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
    def config(self):
        return self.__config

    @property
    def curves(self):
        return self.__sketch.sketchCurves

    @property
    def dimensions(self):
        return self.__sketch.sketchDimensions

    @property
    def directions(self):
        return (self.__xdir, self.__ydir)

    @property
    def face(self):
        return self.__face

    @property
    def geometricConstraints(self):
        return self.__sketch.geometricConstraints

    @property
    def is_visible(self):
        return self.__sketch.isVisible

    @is_visible.setter
    def is_visible(self, val):
        self.__sketch.isVisible = val

    @property
    def length(self):
        return max(self.x_length, self.y_length)

    @property
    def lines(self):
        return self.curves.sketchLines

    @property
    def name(self):
        return self.__name

    @property
    def points(self):
        return self.__sketch.sketchPoints

    @property
    def prefix(self):
        return self.face.name

    @property
    def rectangle(self):
        return self.__rectangle

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

    @property
    def sketch(self):
        return self.__sketch

    @property
    def sketch_alias(self):
        return '{} Finger Sketch'.format(self.name)

    @property
    def vertical(self):
        return self.y_length > self.x_length

    @property
    def width(self):
        return min(self.x_length, self.y_length)

    @property
    def x_direction(self):
        return self.__xdir

    @property
    def x_length(self):
        start = self.__min_point.x
        end = self.__max_point.x
        return end - start

    @property
    def y_direction(self):
        return self.__ydir

    @property
    def y_length(self):
        start = self.__min_point.y
        end = self.__max_point.y
        return end - start
