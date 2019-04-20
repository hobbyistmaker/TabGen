import traceback

from adsk.core import ObjectCollection
from adsk.core import Point3D
from adsk.core import ValueInput
from adsk.fusion import DimensionOrientations
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType
from adsk.fusion import SketchPoint

from ..util import uimessage
from ..util import userDefinedWidthId

from adsk.core import Application

app = Application.get()
ui = app.userInterface

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
HorizontalDimension = DimensionOrientations.HorizontalDimensionOrientation
VerticalDimension = DimensionOrientations.VerticalDimensionOrientation
createByReal = ValueInput.createByReal


def offset(point, offset=0, is_flipped=False, vertical=False):

    if type(point) is SketchPoint:
        o = point.geometry
    else:
        o = point

    ui.messageBox('Offset: {}\nFlipped: {}\nVertical: {}\n'.format(offset, is_flipped, vertical))

    if vertical:
        o.y += offset if is_flipped is False else -offset
    else:
        o.x += offset if is_flipped is False else -offset

    return o


def min_x(line):
    ssp = line.startSketchPoint.geometry
    esp = line.endSketchPoint.geometry
    return ssp if ssp.x < esp.x else esp


def max_x(line):
    ssp = line.startSketchPoint.geometry
    esp = line.endSketchPoint.geometry
    return esp if esp.x > ssp.x else ssp


def min_y(line):
    ssp = line.startSketchPoint.geometry
    esp = line.endSketchPoint.geometry
    return ssp if ssp.y < esp.y else esp


def max_y(line):
    ssp = line.startSketchPoint.geometry
    esp = line.endSketchPoint.geometry
    return esp if esp.y > ssp.y else ssp


class FingerSketch:

    def __init__(self, face, tab_params, ui=None):
        self.__sketch = face.parent.sketches.add(face.bface)

        if tab_params.start_with_tab is False:
            intersectItems = []
            intersectItems.append(face.bface)
            self.__sketch.intersectWithSketchPlane(intersectItems)

        self.__tab_params = tab_params
        self.__face = face
        self.__ui = ui

        profile = self.__sketch.profiles.item(0)
        self.__max_point = profile.boundingBox.maxPoint
        self.__min_point = profile.boundingBox.minPoint

        ui.messageBox('X Length: {}\nY Length: {}\n'.format(self.x_length, self.y_length))

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
        profiles = [self.__sketch.profiles.item(j)
                    for j in range(self.__sketch.profiles.count)]

        if self.vertical:
            if self.flipped_y:
                profiles.sort(key=lambda profile: profile.boundingBox.maxPoint.x)
                profiles.sort(key=lambda profile: profile.boundingBox.maxPoint.y)
            else:
                profiles.sort(key=lambda profile: profile.boundingBox.minPoint.x)
                profiles.sort(key=lambda profile: profile.boundingBox.minPoint.y)
        else:
            if self.flipped_x:
                profiles.sort(key=lambda profile: profile.boundingBox.maxPoint.y)
                profiles.sort(key=lambda profile: profile.boundingBox.maxPoint.x)
            else:
                profiles.sort(key=lambda profile: profile.boundingBox.minPoint.y)
                profiles.sort(key=lambda profile: profile.boundingBox.minPoint.x)

        return profiles

    @property
    def vertical(self):
        return self.y_length > self.x_length

    @property
    def width(self):
        return min(self.x_length, self.y_length)

    @property
    def x_length(self):
        start = self.__min_point.x
        end = self.__max_point.x
        return end - start

    @property
    def y_length(self):
        start = self.__min_point.y
        end = self.__max_point.y
        return end - start

    def draw_finger(self):
        params = self.__tab_params
        width = params.width
        ofs = params.offset

        if params.start_with_tab is False:
            fsp = self.start_point

            if params.finger_type == userDefinedWidthId:
                fep = self.__next_point(fsp, ofs, (self.flipped_x or self.flipped_y))
                self.__draw_rectangle(self.start_point, fsp, fep)

                ssp = self.end_point
                sep = self.__next_point(ssp, -ofs, (self.flipped_x or self.flipped_y))
                self.__draw_rectangle(self.start_point, ssp, sep)

                start_point = offset(self.start_point,
                                     ofs + width,
                                     (self.flipped_x or self.flipped_y),
                                     ref_point=fsp)
            else:
                start_point = fsp
        else:
            start_point = offset(self.start_point,
                                 ofs,
                                 (self.flipped_x or self.flipped_y),
                                 self.vertical)

        end_point = self.__next_point(start_point, width, (self.flipped_x or self.flipped_y))
        self.__draw_rectangle(self.start_point, start_point, end_point)

        self.__sketch.isVisible = False
        return self.profiles

    def __draw_rectangle(self, origin, fp, sp):
        try:
            mark = self.__first_point

            rectangle = self.lines.addTwoPointRectangle(fp, sp)

            line = self.lines.item(0)
            lline1 = 0 if line.length == self.length else 1
            wline1 = 1 if line.length == self.width else 0
            lline2 = lline1 + 2
            wline2 = wline1 + 2

            if self.__tab_params.start_with_tab is True:
                self.geometricConstraints.addCoincident(rectangle.item(0).startSketchPoint,
                                                        self.lines.item(lline1))
                self.geometricConstraints.addCoincident(rectangle.item(2).startSketchPoint,
                                                        self.lines.item(lline2))
                self.dimensions.addDistanceDimension(rectangle.item(0).startSketchPoint,
                                                     rectangle.item(0).endSketchPoint,
                                                     HorizontalDimension,
                                                     Point3D.create(2, -1, 0))
                self.dimensions.addDistanceDimension(rectangle.item(0).startSketchPoint,
                                                     mark,
                                                     HorizontalDimension,
                                                     Point3D.create(3, -1, 0))

                self.geometricConstraints.addHorizontal(rectangle.item(0))
                self.geometricConstraints.addHorizontal(rectangle.item(2))
                self.geometricConstraints.addVertical(rectangle.item(1))
                self.geometricConstraints.addVertical(rectangle.item(3))

            return rectangle

        except:
            uimessage(self.__ui, traceback.format_exc(1))

        return self.lines

    def __next_point(self, point, width, is_flipped=False):
        if self.vertical:
            xwidth = self.x_length
            ywidth = -width if is_flipped is True else width
        else:
            xwidth = -width if is_flipped is True else width
            ywidth = self.y_length

        return Point3D.create(
                    point.x + xwidth,
                    point.y + ywidth,
                    point.z
                )

    @property
    def __first_point(self):
        ssp = self.lines.item(3).endSketchPoint
        esp = self.lines.item(1).startSketchPoint
        sspg = ssp.geometry
        espg = esp.geometry

        if self.vertical:
            if (sspg.y < 0) and(sspg.y < espg.y):
                return esp
            return ssp
        else:
            if (sspg.x < 0) and (sspg.x < espg.x):
                return esp
            return ssp

    @property
    def flipped_x(self):
        line = self.lines.item(0)
        lline1 = 0 if line.length == self.length else 1

        ssp = min_x(self.lines.item(lline1))
        esp = max_x(self.lines.item(lline1 + 2))

        if (ssp.x < 0) and (ssp.x < esp.x):
            return True
        return False

    @property
    def flipped_y(self):
        line = self.lines.item(0)
        lline1 = 0 if line.length == self.length else 1

        ssp = min_y(self.lines.item(lline1))
        esp = max_y(self.lines.item(lline1 + 2))

        if (ssp.y < 0) and (ssp.y < esp.y):
            return True
        return False

    @property
    def __last_point(self):
        # return self.lines.item(1).endSketchPoint
        ssp = self.lines.item(3).endSketchPoint
        esp = self.lines.item(1).startSketchPoint
        sspg = ssp.geometry
        espg = esp.geometry

        if self.vertical:
            if (sspg.y < 0) and(sspg.y < espg.y):
                return ssp
            return esp
        else:
            if (sspg.x < 0) and (sspg.x < espg.x):
                return ssp
            return esp

    @property
    def start_point(self):
        return self.__first_point.geometry

    @property
    def end_point(self):
        return self.__last_point.geometry
