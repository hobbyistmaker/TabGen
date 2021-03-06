import traceback

from collections import namedtuple

from adsk.core import ObjectCollection
from adsk.core import Point3D
from adsk.core import ValueInput as vi
from adsk.fusion import DimensionOrientations as do
from adsk.fusion import FeatureOperations
from adsk.fusion import OffsetStartDefinition
from adsk.fusion import PatternDistanceType
from adsk.fusion import PatternComputeOptions as pco

from .. import definitions as defs
from .. import fusion

CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
HorizontalDimension = do.HorizontalDimensionOrientation
VerticalDimension = do.VerticalDimensionOrientation


class PrimaryAxisMissing(Exception): pass


class FingerManager:

    def __init__(self, inputs, properties, border):
        self.inputs = inputs
        self.face = properties.face
        self.alias = properties.alias
        self.border = border
        self.app = properties.app
        self.ui = properties.ui
        self.name = properties.name
        self.properties = properties

    def configure_secondary_axis(self, input_, secondary, squantity):
        if self.properties.distance_two.value and secondary and secondary.isValid:
            value = abs(self.properties.distance_two.value)
            second_distance = vi.createByReal(value)
            input_.setDirectionTwo(secondary,
                                   vi.createByReal(squantity),
                                   second_distance)

    def constrain_corners(self, sketch, left_corner, right_corner):
        if self.border.is_vertical:
            return self.constrain_vertical_corners(sketch, left_corner, right_corner)
        else:
            return self.constrain_horizontal_corners(sketch, left_corner, right_corner)

    def constrain_finger(self, sketch, finger):
        dimensions = sketch.sketchDimensions
        constraints = sketch.geometricConstraints
        reference = finger.bottom.left.geometry

        if self.border.is_vertical:
            constraints.addVertical(finger.bottom.line)
            constraints.addVertical(finger.top.line)
            constraints.addHorizontal(finger.left.line)
            constraints.addHorizontal(finger.right.line)

            finger_dimension = dimensions.addDistanceDimension(
                finger.top.right.point,
                finger.top.left.point,
                VerticalDimension,
                Point3D.create(reference.x - .5, reference.y + .5, 0)
            )
            offset_dimension = dimensions.addDistanceDimension(
                finger.top.left.point,
                self.border.bottom.left.point,
                VerticalDimension,
                Point3D.create(reference.x - .5, reference.y + .5, 0)
            )

            constraints.addCoincident(
                finger.top.right.point,
                self.border.left.line
            )
            constraints.addCoincident(
                finger.bottom.left.point,
                self.border.right.line
            )
        else:
            constraints.addHorizontal(finger.bottom.line)
            constraints.addHorizontal(finger.top.line)
            constraints.addVertical(finger.left.line)
            constraints.addVertical(finger.right.line)

            finger_dimension = dimensions.addDistanceDimension(
                finger.bottom.left.point,
                finger.bottom.right.point,
                HorizontalDimension,
                Point3D.create(reference.x + .5, reference.y - .5, 0)
            )
            offset_dimension = dimensions.addDistanceDimension(
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

        return finger_dimension, offset_dimension

    def constrain_horizontal_corners(self, sketch, left_corner, right_corner):
        dimensions = sketch.sketchDimensions
        constraints = sketch.geometricConstraints
        lreference = left_corner.bottom.left.geometry
        rreference = right_corner.bottom.left.geometry

        left_dimension = dimensions.addDistanceDimension(
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

        right_dimension = dimensions.addDistanceDimension(
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

        return left_dimension, right_dimension

    def constrain_vertical_corners(self, sketch, left_corner, right_corner):
        dimensions = sketch.sketchDimensions
        constraints = sketch.geometricConstraints
        lreference = left_corner.bottom.left.geometry
        rreference = right_corner.bottom.left.geometry

        left_dimension = dimensions.addDistanceDimension(
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

        right_dimension = dimensions.addDistanceDimension(
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

        return left_dimension, right_dimension

    def create_left_offset_dimension(self, sketch, parameter):
        dimension = sketch.sketchDimensions
        constraints = sketch.geometricConstraints
        lines = sketch.sketchCurves.sketchLines

        start = fusion.next_point(self.border.bottom.left.geometry, parameter.value,
                                  0, self.border.is_vertical)
        end = fusion.next_point(start, 0,
                                self.border.width, self.border.is_vertical)

        line = lines.addByTwoPoints(start, end)
        line.isConstruction = True

        if self.border.is_vertical:
            constraints.addCoincident(
                line.startSketchPoint,
                self.border.right.line
            )
            constraints.addCoincident(
                line.endSketchPoint,
                self.border.left.line
            )
            constraints.addParallel(
                line, self.border.bottom.line
            )
            dimension = dimension.addOffsetDimension(self.border.bottom.line, line,
                                                     Point3D.create(start.x + .5, start.y - .5, 0))
        else:
            constraints.addCoincident(
                line.startSketchPoint,
                self.border.bottom.line
            )
            constraints.addCoincident(
                line.endSketchPoint,
                self.border.top.line
            )
            constraints.addParallel(
                line, self.border.left.line
            )

            dimension = dimension.addOffsetDimension(self.border.left.line, line,
                                                     Point3D.create(start.x + .5, start.y - .5, 0))
        dimension.parameter.name = parameter.name
        if self.properties.parametric and not self.properties.preview_enabled:
            dimension.parameter.expression = parameter.expression
        return dimension

    def draw(self, sketch):
        Properties = namedtuple('Properties', ['finger', 'finger_cut', 'finger_pattern',
                                               'start_dimension',
                                               'corner_cut', 'corner_pattern',
                                               'left_dimension', 'right_dimension',
                                               'finger_dimension', 'sketch'])
        sketch.isComputeDeferred = True
        sketch.name = '{} Finger Sketch'.format(self.name)

        timeline = self.app.activeProduct.timeline

        extrudes = self.inputs.selected_body.parentComponent.features.extrudeFeatures
        body = self.inputs.selected_body
        primary = self.border.reference_line
        secondary = self.get_secondary_axis(sketch)

        start_mp = timeline.markerPosition-1

        for item in self.properties.ordered:
            try:
                self.create_left_offset_dimension(sketch, item)
            except:
                self.ui.messageBox('Error configuring parameter: {} -- {}'.format(item.name, item.expression))
                self.ui.messageBox(traceback.format_exc(3))

        # The finger has to be drawn and extruded first; the operation
        # will fail after the corners are cut, since the edge reference
        # becomes invalid.
        finger, finger_cut, finger_pattern, finger_dimension, start_dimension = self.draw_finger(sketch, extrudes,
                                                                                                 body, primary,
                                                                                                 secondary)

        start_dimension.parameter.expression = self.properties.start.name
        finger_dimension.parameter.expression = self.properties.adjusted_finger_length.name
        finger_pattern.quantityTwo.name = self.properties.interior.name

        sketch.isComputeDeferred = False

        if self.properties.offset.value and not self.properties.tab_first:
            corner_cut, corner_pattern, left_dimension, right_dimension = self.draw_corner(sketch, extrudes, body,
                                                                                           primary, secondary)
            left_dimension.parameter.expression = self.properties.offset.name
        else:
            corner_cut = corner_pattern = left_dimension = right_dimension = None

        # Create a Timeline group to keep things organized
        end_mp = timeline.markerPosition
        tlgroup = timeline.timelineGroups.add(start_mp, end_mp-1)
        tlgroup.name = '{} Finger Group'.format(self.name)

        return Properties(finger, finger_cut, finger_pattern, start_dimension,
                          corner_cut, corner_pattern,
                          left_dimension, right_dimension,
                          finger_dimension, sketch)

    def draw_corner(self, sketch, extrudes, body, primary, secondary):
        left_corner = self.draw_left_corner(sketch)
        right_corner = self.draw_right_corner(sketch)
        corner_cut = self.extrude_corner(body, extrudes, sketch)
        corner_pattern = self.duplicate_corner(body, primary, secondary, corner_cut)

        left_dimension, right_dimension = self.constrain_corners(sketch, left_corner, right_corner)
        return corner_cut, corner_pattern, left_dimension, right_dimension

    def draw_left_corner(self, sketch):
        lines = sketch.sketchCurves.sketchLines
        start = self.border.bottom.left.geometry
        end = fusion.next_point(start, self.properties.offset.value,
                                self.border.width, self.border.is_vertical)

        return fusion.Rectangle(lines.addTwoPointRectangle(start, end))

    def draw_finger(self, sketch, extrudes, body, primary, secondary):
        lines = sketch.sketchCurves.sketchLines
        start = fusion.next_point(self.border.bottom.left.geometry, self.properties.start.value,
                                  0, self.border.is_vertical)
        end = fusion.next_point(start, self.properties.finger_length.value,
                                self.border.width, self.border.is_vertical)

        finger = fusion.Rectangle(lines.addTwoPointRectangle(start, end))
        finger_dimension, offset_dimension = self.constrain_finger(sketch, finger)
        sketch.isComputeDeferred = False
        finger_cut = self.extrude_finger(body, extrudes, sketch, self.properties.edge_margin.value)
        finger_pattern = self.duplicate_finger(body, primary, secondary, finger_cut)
        sketch.isComputeDeferred = True

        return finger, finger_cut, finger_pattern, finger_dimension, offset_dimension

    def draw_right_corner(self, sketch):
        lines = sketch.sketchCurves.sketchLines
        start = fusion.next_point(self.border.bottom.right.geometry,
                                  -self.properties.offset.value, 0, self.border.is_vertical)
        end = fusion.next_point(start, self.properties.offset.value,
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
        # input_.patternComputeOption = pco.IdenticalPatternCompute
        input_.patternComputeOption = pco.AdjustPatternCompute

        self.configure_secondary_axis(input_, secondary, squantity)

        pattern = patterns.add(input_)

        if pattern.healthState > 0:
            pattern.patternComputeOption = pco.AdjustPatternCompute

        pattern.name = name
        return pattern

    def duplicate_corner(self, body, primary, secondary, corner_cut):
        dname = '{} Corner Duplicate Pattern'.format(self.name)
        return self.duplicate(dname, [corner_cut], 1, 0,
                              2, primary, secondary, body)

    def duplicate_finger(self, body, primary, secondary, finger_cut):
        quantity = self.properties.notches.value
        distance = self.properties.pattern_distance.value
        dname = '{} Finger Duplicate Pattern'.format(self.name)
        return self.duplicate(dname, [finger_cut], quantity, distance,
                              self.inputs.interior.value + 2,
                              primary, secondary, body)

    def extrude(self, profiles, body, extrudes, name, edge_offset):
        selection = ObjectCollection.create()

        for profile in profiles:
            selection.add(profile)

        dist = vi.createByReal(-self.properties.adjusted_depth.value)
        cut_input = extrudes.createInput(selection, CFO)
        cut_input.setDistanceExtent(False, dist)
        cut_input.participantBodies = [body]

        if edge_offset:
            offset = OffsetStartDefinition.create(vi.createByReal(-abs(edge_offset)))
            cut_input.startExtent = offset

        cut = extrudes.add(cut_input)
        cut.name = name

        return cut

    def extrude_corner(self, body, extrudes, sketch):
        edge_offset = self.properties.edge_margin.value
        name = '{} Corner Cut Extrude'.format(self.name)
        profiles = [sketch.profiles.item(1), sketch.profiles.item(2)]
        return self.extrude(profiles, body, extrudes, name, edge_offset)

    def extrude_finger(self, body, extrudes, sketch, edge_offset):
        profiles = [sketch.profiles.item(0)]
        cname = '{} Finger Cut Extrude'.format(self.name)
        return self.extrude(profiles, body, extrudes, cname, edge_offset)

    def get_secondary_axis(self, sketch):
        if self.border.is_vertical:
            start = self.border.bottom.left
        else:
            start = self.border.top.left

        secondary = fusion.perpendicular_edge_from_vertex(self.face,
                                                          start.vertex).edge
        if not secondary:
            start = start.geometry
            end = Point3D.create(start.x, start.y, start.z - 10)
            secondary = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
            secondary.isConstruction = True
        return secondary

    def save(self, properties):
        if not self.inputs.parametric:
            self.properties.save(properties)
