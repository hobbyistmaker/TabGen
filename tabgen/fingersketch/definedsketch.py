from adsk.core import Application
from adsk.core import Point3D
from adsk.fusion import DimensionOrientations
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType

from ...util import userDefinedWidthId

from .fingersketch import FingerSketch

app = Application.get()
ui = app.userInterface

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
HorizontalDimension = DimensionOrientations.HorizontalDimensionOrientation
VerticalDimension = DimensionOrientations.VerticalDimensionOrientation


class DefinedSketch(FingerSketch):

    finger_type = userDefinedWidthId

    def start_with_tab(self, fsp, width, offset):
        # Draw finger
        start_point = self.offset(fsp, offset.value)
        end_point = self._next_point(start_point, width.value)
        finger = self._draw_rectangle(fsp, end_point)
        self.set_finger_constraints(finger, width, offset)

    def start_with_notch(self, fsp, width, offset):
        # Draw starting notch
        fep = self._next_point(fsp, offset.value)
        notch1 = self._draw_rectangle(fsp, fep)
        self.set_first_margin_constraint(notch1, offset)

        # Draw ending notch
        ssp = self.rectangle.bottom_right.geometry
        sep = self._next_point(ssp, offset.value)
        notch2 = self._draw_rectangle(sep, ssp)
        self.set_last_margin_constraint(notch2, offset)

        # Draw inside finger
        start_point = self.offset(fsp,
                                  offset.value + width.value)
        end_point = self._next_point(start_point, width.value)
        finger = self._draw_rectangle(start_point, end_point)
        self.set_finger_constraints(finger, width, offset)

    def draw_finger(self):
        offset = self.params.offset
        width = self.params.width

        if self.rectangle.is_vertical:
            fsp = self.rectangle.bottom_right.geometry
        else:
            fsp = self.rectangle.bottom_left.geometry

        new_fsp = (self._draw_margin(fsp).startSketchPoint.geometry
                   if self.params.margin.value > 0 else fsp)

        if self.params.start_with_tab:
            self.start_with_tab(new_fsp, width, offset)
        else:
            self.start_with_notch(new_fsp, width, offset)

        self.params.save_all()
        self.is_visible = False
        return self.profiles()

    def set_finger_constraints(self, rectangle, width, offset):
        self.fingerdim = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            rectangle.bottom_right,
            HorizontalDimension,
            Point3D.create(2, -1, 0))
        width.entity = self.fingerdim.parameter
        width.save(temp=True)

        self.fingeroffset = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            self.rectangle.bottom_left,
            HorizontalDimension,
            Point3D.create(3, -1, 0))
        offset.entity = self.fingeroffset.parameter
        offset.save(temp=True)

        if self.rectangle.is_vertical:
            pass
        else:
            self.geometricConstraints.addCoincident(
                rectangle.bottom_left,
                self.rectangle.bottom.sketch_line)
            self.geometricConstraints.addCoincident(
                rectangle.top_right,
                self.rectangle.top.sketch_line)

    def set_first_margin_constraint(self, rectangle, offset):
        if self.rectangle.is_vertical:
            pass
        else:
            self.geometricConstraints.addCoincident(
                rectangle.top_right,
                self.rectangle.top.sketch_line)

            self.geometricConstraints.addCoincident(
                rectangle.bottom_left,
                self.rectangle.bottom_left)

        self.leftcorner = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            rectangle.bottom_right,
            HorizontalDimension,
            Point3D.create(2, -1, 0))

    def set_last_margin_constraint(self, rectangle, offset):
        if self.rectangle.is_vertical:
            pass
        else:
            self.geometricConstraints.addCoincident(
                rectangle.top_left,
                self.rectangle.top.sketch_line)

            self.geometricConstraints.addCoincident(
                rectangle.bottom_right,
                self.rectangle.bottom_right)

        self.rightcorner = self.dimensions.addDistanceDimension(
            rectangle.bottom_left,
            rectangle.bottom_right,
            HorizontalDimension,
            Point3D.create(2, -1, 0))
