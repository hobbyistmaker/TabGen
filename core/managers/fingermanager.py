from adsk.core import ObjectCollection
from adsk.core import Point3D
from adsk.core import ValueInput as vi
from adsk.fusion import DimensionOrientations as do
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType

from .. import definitions as defs
from .. import fusion

from .automatic import automatic, automatic_params
from .userdefined import user_defined, user_defined_params

CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
HorizontalDimension = do.HorizontalDimensionOrientation
VerticalDimension = do.VerticalDimensionOrientation


class PrimaryAxisMissing(Exception): pass


class FingerManager:

    def __init__(self, config, name, alias, border):
        self.inputs = config.inputs
        self.face = self.inputs.selected_face
        self.alias = alias
        self.border = border
        self.app = config.app
        self.ui = config.ui
        self.name = name

        # We'll create simple numeric fields for use
        # in creating the sketches and patterns. We'll
        # replace with parameters before completing.
        param_finders = {
            defs.automaticWidthId: automatic,
            defs.userDefinedWidthId: user_defined
        }

        param_modifier = {
            defs.automaticWidthId: automatic_params,
            defs.userDefinedWidthId: user_defined_params
        }

        self.params = param_finders[self.inputs.finger_type](self.inputs)
        self.modifier = param_modifier[self.inputs.finger_type]

    def adjust_length(self, sketch, lines):
        dimensions = sketch.sketchDimensions

        left_start = fusion.next_point(self.border.bottom.left.geometry, self.params.margin,
                                       0, self.border.is_vertical)
        left_end = fusion.next_point(left_start, 0,
                                     self.border.width, self.border.is_vertical)

        self.left_adjusted = lines.addByTwoPoints(left_start, left_end)
        self.left_adjusted.isConstruction = True

        right_start = fusion.next_point(left_start, self.params.adjusted_length,
                                        0, self.border.is_vertical)
        right_end = fusion.next_point(right_start, 0,
                                      self.border.width, self.border.is_vertical)

        self.right_adjusted = lines.addByTwoPoints(right_start, right_end)
        self.right_adjusted.isConstruction = True

        self.adjusted_length = dimensions.addDistanceDimension(
            self.left_adjusted.startSketchPoint,
            self.right_adjusted.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )

    def constrain_finger(self, sketch, finger):
        dimensions = sketch.sketchDimensions
        constraints = sketch.geometricConstraints
        reference = finger.bottom.left.geometry

        if self.border.is_vertical:
            constraints.addVertical(self.finger.bottom.line)
            constraints.addVertical(self.finger.top.line)
            constraints.addHorizontal(self.finger.left.line)
            constraints.addHorizontal(self.finger.right.line)

            self.finger_dimension = dimensions.addDistanceDimension(
                finger.bottom.left.point,
                finger.top.left.point,
                VerticalDimension,
                Point3D.create(reference.x - .5, reference.y + .5, 0)
            )
            self.offset_dimension = dimensions.addDistanceDimension(
                finger.bottom.left.point,
                self.border.bottom.left.point,
                VerticalDimension,
                Point3D.create(reference.x - .5, reference.y + .5, 0)
            )

            constraints.addCoincident(
                finger.bottom.right.point,
                self.border.right.line
            )
            constraints.addCoincident(
                finger.top.left.point,
                self.border.left.line
            )
        else:
            constraints.addHorizontal(self.finger.bottom.line)
            constraints.addHorizontal(self.finger.top.line)
            constraints.addVertical(self.finger.left.line)
            constraints.addVertical(self.finger.right.line)

            self.finger_dimension = dimensions.addDistanceDimension(
                finger.bottom.left.point,
                finger.bottom.right.point,
                HorizontalDimension,
                Point3D.create(reference.x + .5, reference.y - .5, 0)
            )
            self.offset_dimension = dimensions.addDistanceDimension(
                finger.bottom.left.point,
                self.border.bottom.left.point,
                HorizontalDimension,
                Point3D.create(reference.x + .5, reference.y - .5, 0)
            )

            constraints.addCoincident(
                finger.bottom.left.point,
                self.border.bottom.line
            )
            constraints.addCoincident(
                finger.top.right.point,
                self.border.top.line
            )

    def constrain_horizontal_corners(self, sketch, left_corner, right_corner):
        dimensions = sketch.sketchDimensions
        constraints = sketch.geometricConstraints
        lreference = left_corner.bottom.left.geometry
        rreference = right_corner.bottom.left.geometry

        self.left_dimension = dimensions.addDistanceDimension(
            left_corner.bottom.left.point,
            left_corner.bottom.right.point,
            HorizontalDimension,
            Point3D.create(lreference.x + .5, lreference.y - .5, 0)
        )
        constraints.addCoincident(
            left_corner.bottom.left.point,
            self.border.bottom.left.point
        )
        constraints.addCoincident(
            left_corner.top.right.point,
            self.border.top.line
        )
        constraints.addHorizontal(left_corner.bottom.line)
        constraints.addHorizontal(left_corner.top.line)
        constraints.addVertical(left_corner.left.line)
        constraints.addVertical(left_corner.right.line)

        self.right_dimension = dimensions.addDistanceDimension(
            right_corner.bottom.left.point,
            right_corner.bottom.right.point,
            HorizontalDimension,
            Point3D.create(rreference.x + .5, rreference.y - .5, 0)
        )
        constraints.addCoincident(
            right_corner.bottom.left.point,
            self.border.bottom.line
        )
        constraints.addCoincident(
            right_corner.top.right.point,
            self.border.top.right.point
        )
        constraints.addHorizontal(right_corner.bottom.line)
        constraints.addHorizontal(right_corner.top.line)
        constraints.addVertical(right_corner.left.line)
        constraints.addVertical(right_corner.right.line)

    def constrain_vertical_corners(self, sketch, left_corner, right_corner):
        dimensions = sketch.sketchDimensions
        constraints = sketch.geometricConstraints
        lreference = left_corner.bottom.left.geometry
        rreference = right_corner.bottom.left.geometry

        self.left_dimension = dimensions.addDistanceDimension(
            left_corner.bottom.left.point,
            left_corner.bottom.right.point,
            HorizontalDimension,
            Point3D.create(lreference.x + .5, lreference.y - .5, 0)
        )
        constraints.addCoincident(
            left_corner.bottom.left.point,
            self.border.bottom.left.point
        )
        constraints.addCoincident(
            left_corner.top.right.point,
            self.border.top.line
        )
        constraints.addHorizontal(left_corner.bottom.line)
        constraints.addHorizontal(left_corner.top.line)
        constraints.addVertical(left_corner.left.line)
        constraints.addVertical(left_corner.right.line)

        self.right_dimension = dimensions.addDistanceDimension(
            right_corner.bottom.left.point,
            right_corner.bottom.right.point,
            HorizontalDimension,
            Point3D.create(rreference.x + .5, rreference.y - .5, 0)
        )
        constraints.addCoincident(
            right_corner.bottom.left.point,
            self.border.bottom.line
        )
        constraints.addCoincident(
            right_corner.top.right.point,
            self.border.top.right.point
        )
        constraints.addHorizontal(right_corner.bottom.line)
        constraints.addHorizontal(right_corner.top.line)
        constraints.addVertical(right_corner.left.line)
        constraints.addVertical(right_corner.right.line)

    def draw(self, sketch):
        lines = sketch.sketchCurves.sketchLines
        timeline = self.app.activeProduct.timeline

        extrudes = self.inputs.selected_body.parentComponent.features.extrudeFeatures
        body = self.inputs.selected_body
        points = self.border.reference_points
        primary = self.border.reference_line
        secondary = fusion.perpendicular_edge_from_vertex(self.inputs.selected_face,
                                                          self.border.top.left.vertex).edge

        start_mp = timeline.markerPosition-1

        self.mark_fingers(sketch, lines)
        self.mark_pattern(sketch, lines)
        self.adjust_length(sketch, lines)
        # The finger has to be drawn and extruded first; the operation
        # will fail after the corners are cut, since the edge reference
        # becomes invalid.
        self.draw_finger(sketch, extrudes, body, primary, secondary)

        if self.params.offset and not self.inputs.tab_first:
            self.draw_corner(sketch, extrudes, body, primary, secondary)

        # Create a Timeline group to keep things organized
        end_mp = timeline.markerPosition
        tlgroup = timeline.timelineGroups.add(start_mp, end_mp-1)
        tlgroup.name = '{} Finger Group'.format(self.name)

        return self

    def save(self):
        if not self.inputs.parametric:
            self.modifier(self.alias,
                          self.app.activeProduct.allParameters,
                          self.app.activeProduct.userParameters,
                          self.inputs,
                          self.finger_dimension, self.offset_dimension,
                          self.finger_cut, self.finger_pattern,
                          self.finger_distance, self.adjusted_length,
                          self.pattern_distance,
                          getattr(self, 'corner_cut', None),
                          getattr(self, 'corner_pattern', None),
                          getattr(self, 'left_dimension', None),
                          getattr(self, 'right_dimension', None))

    def draw_corner(self, sketch, extrudes, body, primary, secondary):
        self.left_corner = self.draw_left_corner(sketch)
        self.right_corner = self.draw_right_corner(sketch)

        self.extrude_corner(body, extrudes, sketch)

        self.duplicate_corner(body, primary, secondary)

        self.constrain_corners(sketch)

    def constrain_corners(self, sketch):
        if self.border.is_vertical:
            self.constrain_vertical_corners(sketch, self.left_corner, self.right_corner)
        else:
            self.constrain_horizontal_corners(sketch, self.left_corner, self.right_corner)

    def duplicate_corner(self, body, primary, secondary):
        dname = '{} Corner Duplicate Pattern'.format(self.name)
        self.corner_pattern = self.duplicate(dname, [self.corner_cut], 1, 0,
                                             2, primary, secondary, body)

    def extrude_corner(self, body, extrudes, sketch):
        name = '{} Corner Cut Extrude'.format(self.name)
        profiles = [sketch.profiles.item(1), sketch.profiles.item(2)]
        self.corner_cut = self.extrude(profiles, body, extrudes, name)

    def draw_finger(self, sketch, extrudes, body, primary, secondary):
        lines = sketch.sketchCurves.sketchLines
        start = fusion.next_point(self.border.bottom.left.geometry, self.params.start,
                                  0, self.border.is_vertical)
        end = fusion.next_point(start, self.params.finger_length,
                                self.border.width, self.border.is_vertical)

        self.finger = fusion.Rectangle(lines.addTwoPointRectangle(start, end))
        self.constrain_finger(sketch, self.finger)
        self.finger_cut = self.exrude_finger(body, extrudes, sketch)
        self.finger_pattern = self.duplicate_finger(body, primary, secondary)

    def duplicate_finger(self, body, primary, secondary):
        quantity = self.params.notches
        distance = self.params.pattern_distance
        dname = '{} Finger Duplicate Pattern'.format(self.name)
        return self.duplicate(dname, [self.finger_cut], quantity, distance,
                                      self.inputs.interior.value + 2,
                                      primary, secondary, body)

    def exrude_finger(self, body, extrudes, sketch):
        profiles = [sketch.profiles.item(0)]
        cname = '{} Finger Cut Extrude'.format(self.name)
        return self.extrude(profiles, body, extrudes, cname)

    def draw_left_corner(self, sketch):
        lines = sketch.sketchCurves.sketchLines
        start = self.border.bottom.left.geometry
        end = fusion.next_point(start, self.params.offset,
                                self.border.width, self.border.is_vertical)

        return fusion.Rectangle(lines.addTwoPointRectangle(start, end))

    def draw_right_corner(self, sketch):
        lines = sketch.sketchCurves.sketchLines
        start = fusion.next_point(self.border.bottom.right.geometry,
                                  -self.params.offset, 0, self.border.is_vertical)
        end = fusion.next_point(start, self.params.offset,
                                self.border.width, self.border.is_vertical)

        return fusion.Rectangle(lines.addTwoPointRectangle(start, end))

    def duplicate(self, name, features, quantity, distance,
                  squantity, primary, secondary, body):

        if not primary or not primary.isValid:
            raise PrimaryAxisMissing

        entities = ObjectCollection.create()
        for feature in features:
            entities.add(feature)

        patterns = body.parentComponent.features.rectangularPatternFeatures

        quantity = vi.createByReal(quantity)
        distance = vi.createByReal(distance)

        input_ = patterns.createInput(entities, primary, quantity, distance, EDT)

        self.configure_secondary_axis(input_, secondary, squantity)

        pattern = patterns.add(input_)
        pattern.name = name
        return pattern

    def configure_secondary_axis(self, input_, secondary, squantity):
        if self.params.distance > 0 and secondary and secondary.isValid:
            second_distance = vi.createByReal(self.params.distance - self.params.depth)
            input_.setDirectionTwo(secondary,
                                   vi.createByReal(squantity),
                                   second_distance)

    def extrude(self, profiles, body, extrudes, name):
        selection = ObjectCollection.create()

        for profile in profiles:
            selection.add(profile)

        dist = vi.createByReal(-abs(self.params.depth))
        cut_input = extrudes.createInput(selection, CFO)
        cut_input.setDistanceExtent(False, dist)
        cut_input.participantBodies = [body]

        cut = extrudes.add(cut_input)
        cut.name = name

        return cut

    def mark_fingers(self, sketch, lines):
        dimensions = sketch.sketchDimensions

        left_start = fusion.next_point(self.border.bottom.left.geometry, self.params.offset,
                                       0, self.border.is_vertical)
        left_end = fusion.next_point(left_start, 0,
                                     self.border.width, self.border.is_vertical)

        self.left_marker = lines.addByTwoPoints(left_start, left_end)
        self.left_marker.isConstruction = True

        right_start = fusion.next_point(left_start, self.params.finger_distance,
                                        0, self.border.is_vertical)
        right_end = fusion.next_point(right_start, 0,
                                      self.border.width, self.border.is_vertical)

        self.right_marker = lines.addByTwoPoints(right_start, right_end)
        self.right_marker.isConstruction = True

        self.finger_distance = dimensions.addDistanceDimension(
            self.left_marker.startSketchPoint,
            self.right_marker.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )

    def mark_pattern(self, sketch, lines):
        dimensions = sketch.sketchDimensions

        width = self.params.finger_length * (2 if self.inputs.tab_first else 1)
        left_start = fusion.next_point(self.border.bottom.left.geometry, width,
                                       0, self.border.is_vertical)
        left_end = fusion.next_point(left_start, 0,
                                     self.border.width, self.border.is_vertical)

        self.left_pattern = lines.addByTwoPoints(left_start, left_end)
        self.left_pattern.isConstruction = True

        right_start = fusion.next_point(left_start, self.params.pattern_distance,
                                        0, self.border.is_vertical)
        right_end = fusion.next_point(right_start, 0,
                                      self.border.width, self.border.is_vertical)

        self.right_pattern = lines.addByTwoPoints(right_start, right_end)
        self.right_pattern.isConstruction = True

        self.pattern_offset = dimensions.addDistanceDimension(
            self.left_marker.startSketchPoint,
            self.left_pattern.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )

        self.pattern_distance = dimensions.addDistanceDimension(
            self.left_pattern.startSketchPoint,
            self.right_pattern.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )
