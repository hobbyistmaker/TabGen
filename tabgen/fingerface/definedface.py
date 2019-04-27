from adsk.core import Application
from adsk.core import Line3D
from adsk.core import ObjectCollection
from adsk.core import Plane
from adsk.core import ValueInput
from adsk.fusion import Design
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType

from ...util import userDefinedWidthId
from ..fingersketch import FingerSketch
from .fingerface import FingerFace
from .fingerparams import FingerParams
from .fingerpattern import FingerPattern

app = Application.get()
ui = app.userInterface
design = Design.cast(app.activeProduct)

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
createByReal = ValueInput.createByReal
createByString = ValueInput.createByString


def parallel_face(faces, reference, point):
    refplane = Plane.cast(reference.geometry)
    # ui.messageBox('{} faces found.'.format(faces.count))
    for j in range(0, faces.count):
        face = faces.item(j)
        if face == reference:
            continue

        otherplane = Plane.cast(face.geometry)
        if otherplane.isParallelToPlane(refplane):
            # ui.messageBox('found parallel face')
            vertices = face.vertices
            for i in range(0, vertices.count):
                vertexp = vertices.item(i).geometry
                if vertexp.isEqualTo(point):
                    # ui.messageBox('Vertex: {} {} {}\nPoint: {} {} {}'.format(vertexp.x, vertexp.y, vertexp.z, point.x, point.y, point.z))
                    return face
    # ui.messageBox('no parallel face found')


def edge_matches_point(edge, point):
    edge_start = edge.startVertex.geometry
    edge_end = edge.endVertex.geometry

    if edge_start.isEqualTo(point) or edge_end.isEqualTo(point):
        return True
    return False


class DefinedFace(FingerFace):

    finger_type = userDefinedWidthId

    def extrude(self, tc):
        default_finger_count = int(self.length // tc.default_width.value)
        default_tab_count = int(self.length // (2 * tc.default_width.value))
        tab_length = 2 * tc.default_width.value * default_tab_count
        margin = (self.length - tab_length + tc.default_width.value) / 2
        default_width = tc.default_width.value

        if tc.start_with_tab is True:
            distance = self.length - margin * 2 - default_width
            extrude_count = default_tab_count
        else:
            distance = self.length - margin * 2 - default_width*3
            extrude_count = default_tab_count - 1

        tab_width = tc.default_width.value

        params = FingerParams(tc.finger_type,
                              tc.start_with_tab,
                              tc.edge,
                              default_finger_count,
                              tc.default_width,
                              tab_width,
                              tc.depth,
                              extrude_count,
                              distance,
                              margin,
                              tc.parametric)
        sketch = FingerSketch.create(tc.finger_type, self, params, self._ui)

        # We need to save some information for future reference,
        # since the underlying data will change once any changes are
        # made to the associated BRepFace

        # We save the top_line of the sketch to use as a reference
        # for the rectangularPattern axis 1, and then find the
        # perpendicular edge that attaches to the top right point
        # of the sketch to use as a reference for axis 2
        join_point = sketch.reference_points
        primary_axis = sketch.reference_line.sketch_line
        secondary_axis, secondary_point = self.perpendicular_edge_from_point(join_point)

        profiles = sketch.draw_finger()
        pattern_params = FingerPattern(params.distance,
                                       tc.distance,
                                       params.notches,
                                       params.depth,
                                       params.offset)

        profs = ObjectCollection.create()
        finger_idx = 1 if tc.start_with_tab and len(profiles) > 1 else 2
        profs.add(profiles[finger_idx])

        if len(profiles) > 0:
            finger = self._extrude_finger(tc.depth, profs, sketch.parameters)
            self._duplicate_fingers(pattern_params, finger, primary_axis,
                                    secondary_axis, tc.edge, sketch)
            profs.clear()

            if not tc.start_with_tab:
                profs.add(profiles[0])
                profs.add(profiles[4])
                corners = self._extrude_finger(tc.depth, profs, sketch.parameters)

                if tc.edge is not None:
                    corner_params = FingerPattern(params.distance, tc.distance,
                                                  params.notches, params.depth, params.offset)
                    other_face = parallel_face(self.body.faces, sketch.reference_plane, secondary_point)
                    newpoints = (secondary_point, None)
                    corner_axis, spoint = self.perpendicular_edge_from_point(newpoints, face=other_face)
                    if corner_axis:
                        self._duplicate_corners(corner_params, corners,
                                                corner_axis, tc.edge, sketch)

            if self._timeline and self._timeline.isValid:
                mp = self._timeline.markerPosition
                tcount = self._timeline.count - 1
                pos = mp if mp <= tcount else tcount
                tloffset = 2 if tc.start_with_tab else 4
                tlgroup = self._timeline.timelineGroups.add(pos-tloffset, pos)
                if sketch.parameters:
                    tlgroup.name = '{} Finger Group'.format(sketch.parameters.name)

    def _duplicate_corners(self, params, feature, primary, secondary,
                           sketch=None):

        parameters = sketch.parameters
        quantity = createByReal(2)

        inputEntities = ObjectCollection.create()
        inputEntities.add(feature)

        sdistance = abs(params.distance_two.value)
        if parameters is not None:
            parameters.add_far_length(sdistance)
            parallel_distance = createByString(parameters.distance_two.name)
        else:
            parallel_distance = createByReal(-(sdistance - params.depth.value))

        patternInput = self.patterns.createInput(inputEntities,
                                                 primary,
                                                 quantity,
                                                 parallel_distance,
                                                 EDT)

        if secondary is not None:
            patternInput.setDirectionTwo(secondary,
                                         createByReal(1),
                                         createByReal(0))

        try:
            # patternInput.patternComputeOption = 1
            pattern = self.patterns.add(patternInput)
            if parameters is not None:
                pattern.name = '{} Corner Rectangle Pattern'.format(parameters.name)
            return pattern
        except:
            uimessage(traceback.format_exc())

