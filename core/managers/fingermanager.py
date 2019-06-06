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

from .automatic import automatic, automatic_params
from .constantwidth import user_defined, user_defined_params

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

    def mark_adjusted_distance(self, sketch):
        AdjustedMarker = namedtuple('AdjustedMarker', ['left', 'distance', 'fingers',
                                                       'face_length', 'second_distance', 'default_width'])

        # adjusted_length, adjusted_margin, left_start, right_adjusted = self.dimension_adjusted_length(sketch)
        # finger_count = self.dimension_finger_count(left_start, sketch)
        # face_length = self.dimension_face_length(left_start, sketch)
        # second_distance = self.dimension_secondary_distance(left_start, sketch)
        # default_width = self.dimension_default_width(left_start, sketch)

        left_adjusted, left = self.create_left_offset_dimension(sketch, self.properties.margin.value)
        adjusted_length, right = self.create_left_offset_dimension(sketch, self.properties.adjusted_length.value)
        finger_count, count_line = self.create_left_offset_dimension(sketch, self.properties.fingers.value)
        face_length, face_line = self.create_left_offset_dimension(sketch, self.properties.face_length.value)
        second_distance, second_line = self.create_left_offset_dimension(sketch, self.properties.distance_two.value)
        default_width, width_line = self.create_left_offset_dimension(sketch, self.properties.default_width.value)

        return AdjustedMarker(left_adjusted, adjusted_length,
                              finger_count, face_length, second_distance, default_width)

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
                start,
                self.border.left.line
            )
            constraints.addCoincident(
                end,
                self.border.right.line
            )
            constraints.addParallel(
                line, self.border.bottom.line
            )
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
        return dimension

    def create_right_offset_dimension(self, sketch, value):
        dimension = sketch.sketchDimensions
        constraints = sketch.geometricConstraints
        lines = sketch.sketchCurves.sketchLines

        start = fusion.next_point(self.border.bottom.right.geometry, -value,
                                  0, self.border.is_vertical)
        end = fusion.next_point(start, 0,
                                self.border.width, self.border.is_vertical)

        line = lines.addByTwoPoints(start, end)
        line.isConstruction = True

        if self.border.is_vertical:
            constraints.addCoincident(
                start,
                self.border.right.line
            )
            constraints.addCoincident(
                end,
                self.border.left.line
            )
            constraints.addParallel(
                line, self.border.bottom.line
            )
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

        return dimension.addOffsetDimension(self.border.right.line, line,
                                            Point3D.create(start.x + .5, start.y - .5, 0)), line

    def dimension_adjusted_length(self, sketch):
        lines = sketch.sketchCurves.sketchLines
        dimensions = sketch.sketchDimensions
        left_adjusted, left_start = self.mark_left_margin(lines)
        right_adjusted = self.mark_right_margin(left_start, lines)
        adjusted_length = dimensions.addDistanceDimension(
            left_adjusted.startSketchPoint,
            right_adjusted.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )
        adjusted_margin = dimensions.addDistanceDimension(
            self.border.bottom.left.point,
            left_adjusted.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )
        return adjusted_length, adjusted_margin, left_start, right_adjusted

    def dimension_finger_count(self, left_start, sketch):
        lines = sketch.sketchCurves.sketchLines
        dimensions = sketch.sketchDimensions
        count_start = fusion.next_point(self.border.bottom.left.geometry, 0,
                                        -self.border.width, self.border.is_vertical)
        count_end = fusion.next_point(count_start, self.properties.fingers.value,
                                      0, self.border.is_vertical)
        left_count = lines.addByTwoPoints(count_start, count_end)
        left_count.isConstruction = True
        finger_count = dimensions.addDistanceDimension(
            self.border.bottom.left.point,
            left_count.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )
        return finger_count

    def dimension_face_length(self, left_start, sketch):
        lines = sketch.sketchCurves.sketchLines
        dimensions = sketch.sketchDimensions
        face_start = fusion.next_point(self.border.top.left.geometry, 0,
                                       self.border.width, self.border.is_vertical)
        face_end = fusion.next_point(face_start, self.properties.face_length.value,
                                     0, self.border.is_vertical)
        face_line = lines.addByTwoPoints(face_start, face_end)
        face_line.isConstruction = True
        face_length = dimensions.addDistanceDimension(
            face_line.startSketchPoint,
            face_line.endSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )
        return face_length

    def dimension_secondary_distance(self, left_start, sketch):
        lines = sketch.sketchCurves.sketchLines
        dimensions = sketch.sketchDimensions
        second_start = fusion.next_point(self.border.top.left.geometry, 0,
                                         self.border.width * 2, self.border.is_vertical)
        second_end = fusion.next_point(second_start, self.properties.distance.value, 0,
                                       self.border.is_vertical)
        second_line = lines.addByTwoPoints(second_start, second_end)
        second_line.isConstruction = True
        second_distance = dimensions.addDistanceDimension(
            second_line.startSketchPoint,
            second_line.endSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )
        return second_distance

    def dimension_default_width(self, left_start, sketch):
        lines = sketch.sketchCurves.sketchLines
        dimensions = sketch.sketchDimensions
        dwidth_start = fusion.next_point(self.border.top.left.geometry, 0,
                                         self.border.width * 3, self.border.is_vertical)
        dwidth_end = fusion.next_point(dwidth_start, self.properties.default_width.value, 0,
                                       self.border.is_vertical)
        dwidth_line = lines.addByTwoPoints(dwidth_start, dwidth_end)
        dwidth_line.isConstruction = True
        default_width = dimensions.addDistanceDimension(
            dwidth_line.startSketchPoint,
            dwidth_line.endSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )
        return default_width

    def mark_right_margin(self, left_start, lines):
        right_start = fusion.next_point(left_start, self.properties.adjusted_length.value,
                                        0, self.border.is_vertical)
        right_end = fusion.next_point(right_start, 0,
                                      self.border.width, self.border.is_vertical)
        right_adjusted = lines.addByTwoPoints(right_start, right_end)
        right_adjusted.isConstruction = True
        return right_adjusted

    def mark_left_margin(self, lines):
        left_start = fusion.next_point(self.border.bottom.left.geometry, self.properties.margin.value,
                                       0, self.border.is_vertical)
        left_end = fusion.next_point(left_start, 0,
                                     self.border.width, self.border.is_vertical)
        left_adjusted = lines.addByTwoPoints(left_start, left_end)
        left_adjusted.isConstruction = True
        return left_adjusted, left_start

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
                finger.bottom.left.point,
                finger.top.left.point,
                VerticalDimension,
                Point3D.create(reference.x - .5, reference.y + .5, 0)
            )
            offset_dimension = dimensions.addDistanceDimension(
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

    def draw(self, sketch):
        Properties = namedtuple('Properties', ['finger_distance', 'adjusted_length', 'pattern_distance', 'distance',
                                               'default_width', 'face_length', 'second_distance',
                                               'finger_count', 'finger', 'finger_cut', 'finger_pattern',
                                               'finger_length', 'start_dimension', 'offset_dimension',
                                               'corner_cut', 'corner_pattern', 'default_depth', 'adjusted_depth',
                                               'left_dimension', 'right_dimension', 'adjusted_finger_length',
                                               'finger_dimension', 'margin', 'kerf', 'sketch', 'edge_margin'])
        sketch.isComputeDeferred = True
        timeline = self.app.activeProduct.timeline

        extrudes = self.inputs.selected_body.parentComponent.features.extrudeFeatures
        body = self.inputs.selected_body
        primary = self.border.reference_line
        secondary = fusion.perpendicular_edge_from_vertex(self.face,
                                                          self.border.top.left.vertex).edge

        start_mp = timeline.markerPosition-1

        margin = self.create_left_offset_dimension(sketch, self.properties.margin)
        edge_margin = self.create_left_offset_dimension(sketch, self.properties.edge_margin)
        kerf = self.create_left_offset_dimension(sketch, self.properties.kerf)
        default_depth = self.create_left_offset_dimension(sketch, self.properties.depth)
        adjusted_length = self.create_left_offset_dimension(sketch, self.properties.adjusted_length)
        adjusted_depth = self.create_left_offset_dimension(sketch, self.properties.adjusted_depth)
        adjusted_finger_length = self.create_left_offset_dimension(sketch, self.properties.adjusted_finger_length)
        finger_count = self.create_left_offset_dimension(sketch, self.properties.fingers)
        finger_length = self.create_left_offset_dimension(sketch, self.properties.finger_length)
        face_length = self.create_left_offset_dimension(sketch, self.properties.face_length)
        distance = self.create_left_offset_dimension(sketch, self.properties.distance)
        second_distance = self.create_left_offset_dimension(sketch, self.properties.distance_two)
        default_width = self.create_left_offset_dimension(sketch, self.properties.default_width)
        offset_dimension = self.create_left_offset_dimension(sketch, self.properties.offset)
        finger_distance = self.create_left_offset_dimension(sketch, self.properties.finger_distance)
        pattern_distance = self.create_left_offset_dimension(sketch, self.properties.pattern_distance)

        # The finger has to be drawn and extruded first; the operation
        # will fail after the corners are cut, since the edge reference
        # becomes invalid.
        finger, finger_cut, finger_pattern, finger_dimension, start_dimension = self.draw_finger(sketch, extrudes, body, primary, secondary)

        start_dimension.parameter.name = self.properties.start.name
        finger_dimension.parameter.expression = self.properties.adjusted_finger_length.name
        finger_pattern.quantityTwo.name = self.properties.interior.name

        sketch.isComputeDeferred = False

        if self.properties.offset.value and not self.properties.tab_first:
            corner_cut, corner_pattern, left_dimension, right_dimension = self.draw_corner(sketch, extrudes, body, primary, secondary)
            left_dimension.parameter.name = self.properties.offset.name
        else:
            corner_cut = corner_pattern = left_dimension = right_dimension = None

        # Create a Timeline group to keep things organized
        end_mp = timeline.markerPosition
        tlgroup = timeline.timelineGroups.add(start_mp, end_mp-1)
        tlgroup.name = '{} Finger Group'.format(self.name)

        return Properties(finger_distance, adjusted_length, pattern_distance, distance,
                          default_width, face_length, second_distance, finger_count,
                          finger, finger_cut, finger_pattern, finger_length, start_dimension,
                          offset_dimension, corner_cut, corner_pattern, default_depth, adjusted_depth,
                          left_dimension, right_dimension, adjusted_finger_length,
                          finger_dimension, margin, kerf, sketch, edge_margin)

    def save(self, properties):
        if not self.inputs.parametric:
            self.properties.save(properties)

    def draw_corner(self, sketch, extrudes, body, primary, secondary):
        left_corner = self.draw_left_corner(sketch)
        right_corner = self.draw_right_corner(sketch)
        corner_cut = self.extrude_corner(body, extrudes, sketch)
        corner_pattern = self.duplicate_corner(body, primary, secondary, corner_cut)

        left_dimension, right_dimension = self.constrain_corners(sketch, left_corner, right_corner)
        return corner_cut, corner_pattern, left_dimension, right_dimension

    def constrain_corners(self, sketch, left_corner, right_corner):
        if self.border.is_vertical:
            return self.constrain_vertical_corners(sketch, left_corner, right_corner)
        else:
            return self.constrain_horizontal_corners(sketch, left_corner, right_corner)

    def duplicate_corner(self, body, primary, secondary, corner_cut):
        dname = '{} Corner Duplicate Pattern'.format(self.name)
        return self.duplicate(dname, [corner_cut], 1, 0,
                              2, primary, secondary, body)

    def extrude_corner(self, body, extrudes, sketch):
        name = '{} Corner Cut Extrude'.format(self.name)
        profiles = [sketch.profiles.item(1), sketch.profiles.item(2)]
        return self.extrude(profiles, body, extrudes, name)

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

    def duplicate_finger(self, body, primary, secondary, finger_cut):
        quantity = self.properties.notches.value
        distance = self.properties.pattern_distance.value
        dname = '{} Finger Duplicate Pattern'.format(self.name)
        return self.duplicate(dname, [finger_cut], quantity, distance,
                              self.inputs.interior.value + 2,
                              primary, secondary, body)

    def extrude_finger(self, body, extrudes, sketch, edge_offset):
        profiles = [sketch.profiles.item(0)]
        cname = '{} Finger Cut Extrude'.format(self.name)
        return self.extrude(profiles, body, extrudes, cname, edge_offset)

    def draw_left_corner(self, sketch):
        lines = sketch.sketchCurves.sketchLines
        start = self.border.bottom.left.geometry
        end = fusion.next_point(start, self.properties.offset.value,
                                self.border.width, self.border.is_vertical)

        return fusion.Rectangle(lines.addTwoPointRectangle(start, end))

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
        input_.patternComputeOption = pco.IdenticalPatternCompute

        self.configure_secondary_axis(input_, secondary, squantity)

        pattern = patterns.add(input_)
        pattern.name = name
        return pattern

    def configure_secondary_axis(self, input_, secondary, squantity):
        if self.properties.distance_two.value and secondary and secondary.isValid:
            value = abs(self.properties.distance_two.value)
            second_distance = vi.createByReal(value)
            input_.setDirectionTwo(secondary,
                                   vi.createByReal(squantity),
                                   second_distance)

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

    def mark_finger_distance(self, sketch):
        left_marker, _ = self.create_left_offset_dimension(sketch, self.properties.offset.value)
        right_marker, _ = self.create_left_offset_dimension(sketch, self.properties.finger_distance.value)

        FingerMarker = namedtuple('FingerMarker', ['left', 'right', 'distance'])
        lines = sketch.sketchCurves.sketchLines
        dimensions = sketch.sketchDimensions

        left_start = fusion.next_point(start=self.border.bottom.left.geometry,
                                       length=self.properties.offset.value,
                                       width=0,
                                       vertical=self.border.is_vertical)
        left_end = fusion.next_point(start=left_start,
                                     length=0,
                                     width=self.border.width,
                                     vertical=self.border.is_vertical)

        left_marker = lines.addByTwoPoints(left_start, left_end)
        left_marker.isConstruction = True

        right_start = fusion.next_point(left_start, self.properties.finger_distance.value,
                                        0, self.border.is_vertical)
        right_end = fusion.next_point(right_start, 0,
                                      self.border.width, self.border.is_vertical)

        right_marker = lines.addByTwoPoints(right_start, right_end)
        right_marker.isConstruction = True

        finger_distance = dimensions.addDistanceDimension(
            left_marker.startSketchPoint,
            right_marker.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )

        return FingerMarker(left_marker, right_marker, finger_distance)

    def mark_pattern_distance(self, sketch, left_marker):
        PatternMarker = namedtuple('PatternMarker', ['left', 'right', 'distance'])
        lines = sketch.sketchCurves.sketchLines
        dimensions = sketch.sketchDimensions

        width = self.properties.finger_length.value * (2 if self.properties.tab_first else 1)
        left_start = fusion.next_point(self.border.bottom.left.geometry, width,
                                       0, self.border.is_vertical)
        left_end = fusion.next_point(left_start, 0,
                                     self.border.width, self.border.is_vertical)

        left_pattern = lines.addByTwoPoints(left_start, left_end)
        left_pattern.isConstruction = True

        right_start = fusion.next_point(left_start, self.properties.pattern_distance.value,
                                        0, self.border.is_vertical)
        right_end = fusion.next_point(right_start, 0,
                                      self.border.width, self.border.is_vertical)

        right_pattern = lines.addByTwoPoints(right_start, right_end)
        right_pattern.isConstruction = True

        pattern_distance = dimensions.addDistanceDimension(
            left_pattern.startSketchPoint,
            right_pattern.startSketchPoint,
            HorizontalDimension,
            Point3D.create(left_start.x + .5, left_start.y - .5, 0)
        )

        return PatternMarker(left_pattern, right_pattern, pattern_distance)
