from adsk.core import Application
from adsk.core import Point3D
from adsk.fusion import DimensionOrientations
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType

from ...util import userDefinedWidthId

from .fingersketch import FingerSketch

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
HorizontalDimension = DimensionOrientations.HorizontalDimensionOrientation
VerticalDimension = DimensionOrientations.VerticalDimensionOrientation

app = Application.get()
ui = app.userInterface


class DefinedSketch(FingerSketch):

    finger_type = userDefinedWidthId

    def start_with_tab(self, fsp, width, offset):
        # Draw finger
        start_point = self.offset(fsp, offset)
        end_point = self._next_point(start_point, width)
        finger = self._draw_rectangle(fsp, end_point)
        self.set_finger_constraints(finger, self.params.width)

    def start_with_notch(self, fsp, width, offset):
        ssp = self.rectangle.top_right.geometry

        ui.messageBox('fsp: {} {} {}\nssp: {} {} {}'.format(fsp.x, fsp.y, fsp.z, ssp.x, ssp.y, ssp.z))

        # Draw starting notch
        fep = self._next_point(fsp, offset)
        notch1 = self._draw_rectangle(fsp, fep)
        self.set_first_margin_constraint(notch1)

        # Draw ending notch
        sep = self._next_point(ssp, offset)
        notch2 = self._draw_rectangle(sep, ssp)
        self.set_last_margin_constraint(notch2)

        # Draw inside finger
        start_point = self.offset(fsp,
                                  offset + width)
        end_point = self._next_point(start_point, width)
        finger = self._draw_rectangle(start_point, end_point)
        self.set_finger_constraints(finger, self.params.width)

    def draw_finger(self):
        offset = self.params.offset
        width = self.params.width

        fsp = self.rectangle.bottom_left.geometry

        if self.params.start_with_tab:
            self.start_with_tab(fsp, width, offset)
        else:
            self.start_with_notch(fsp, width, offset)

        self.is_visible = False
        return self.profiles

    def set_finger_constraints(self, rectangle, width):
        tabdim = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            rectangle.bottom_right,
            HorizontalDimension,
            Point3D.create(2, -1, 0))
        # tabdim.parameter.value = width

        self.geometricConstraints.addCoincident(
            rectangle.top_right,
            self.rectangle.top.sketch_line)

        margindim = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            self.rectangle.bottom_left,
            HorizontalDimension,
            Point3D.create(3, -1, 0))
        # margindim.parameter.value = self.params.offset

        if self.params.parametric:
            margindim.parameter.expression = self.parameters.foffset.name
            tabdim.parameter.expression = self.parameters.fingerw.name

        if self.params.start_with_tab is True:
            self.geometricConstraints.addCoincident(
                rectangle.bottom_left,
                self.rectangle.bottom_left)
        else:
            self.geometricConstraints.addCoincident(
                rectangle.bottom_left,
                self.rectangle.bottom.sketch_line)

    def set_first_margin_constraint(self, rectangle):
        tabdim = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            rectangle.bottom_right,
            HorizontalDimension,
            Point3D.create(2, -1, 0))
        # tabdim.parameter.value = self.params.offset

        self.geometricConstraints.addCoincident(
            rectangle.bottom_left,
            self.rectangle.bottom_left)

        self.geometricConstraints.addCoincident(
            rectangle.top_right,
            self.rectangle.top.sketch_line)

        if self.params.parametric:
            tabdim.parameter.expression = self.parameters.foffset.name

    def set_last_margin_constraint(self, rectangle):
        tabdim = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            rectangle.bottom_right,
            HorizontalDimension,
            Point3D.create(2, -1, 0))

        if self.params.parametric:
            tabdim.parameter.expression = self.parameters.foffset.name

        self.geometricConstraints.addCoincident(
            rectangle.bottom_right,
            self.rectangle.bottom_right)
        self.geometricConstraints.addCoincident(
            rectangle.top_left,
            self.rectangle.top.sketch_line)
