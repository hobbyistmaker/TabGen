from adsk.core import Application
from adsk.core import Point3D
from adsk.fusion import DimensionOrientations
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType

from ...util import automaticWidthId
from .fingersketch import FingerSketch

app = Application.get()
ui = app.userInterface

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
HorizontalDimension = DimensionOrientations.HorizontalDimensionOrientation
VerticalDimension = DimensionOrientations.VerticalDimensionOrientation


def display_line(line, title):
    spg = line.startSketchPoint.geometry
    epg = line.endSketchPoint.geometry

    ui.messageBox('Start Point\nX: {} -- Y: {} -- Z: {}\n\nEnd Point\nX: {} -- Y: {} -- Z: {}'.format(spg.x, spg.y, spg.z, epg.x, epg.y, epg.z), title)


class AutoSketch(FingerSketch):

    finger_type = automaticWidthId

    def draw_finger(self):
        params = self.params
        width = params.width
        ofs = params.offset

        fsp = self.rectangle.bottom_left.geometry

        if params.start_with_tab is False:
            start_point = fsp
        else:
            start_point = self.offset(fsp, ofs)

        end_point = self._next_point(start_point, width)
        rectangle = self._draw_rectangle(start_point, end_point)

        self._set_corner_constraints(rectangle)
        self.set_finger_constraints(rectangle)

        self.is_visible = False
        return self.profiles

    def set_finger_constraints(self, rectangle):
        tabdim = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            rectangle.bottom_right,
            HorizontalDimension,
            Point3D.create(2, -1, 0))
        tabdim.parameter.value = self.params.width

        if self.params.parametric:
            tabdim.parameter.expression = self.parameters.fingerw.name

        if self.params.start_with_tab is True:
            margindim = self.dimensions.addDistanceDimension(
                rectangle.bottom_left,
                self.rectangle.bottom_left,
                HorizontalDimension,
                Point3D.create(3, -1, 0))
            margindim.parameter.value = self.params.offset

            if self.params.parametric:
                margindim.parameter.expression = self.parameters.foffset.name
        else:
            self.geometricConstraints.addCoincident(
                rectangle.bottom_left,
                self.rectangle.bottom_left)

    def _set_corner_constraints(self, rectangle):
        if self.params.start_with_tab is False:
            self.geometricConstraints.addCoincident(
                rectangle.bottom_left,
                self.rectangle.bottom.sketch_line)
        self.geometricConstraints.addCoincident(
            rectangle.top_right,
            self.rectangle.top.sketch_line)
