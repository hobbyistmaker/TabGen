import math
import traceback

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
    for j in range(0, faces.count):
        face = faces.item(j)
        if face == reference:
            continue

        otherplane = Plane.cast(face.geometry)
        if otherplane.isParallelToPlane(refplane):
            vertices = face.vertices
            for i in range(0, vertices.count):
                vertexp = vertices.item(i).geometry
                if vertexp.isEqualTo(point):
                    return face


def edge_matches_point(edge, point):
    edge_start = edge.startVertex.geometry
    edge_end = edge.endVertex.geometry

    if edge_start.isEqualTo(point) or edge_end.isEqualTo(point):
        return True
    return False


class DefinedFace(FingerFace):

    finger_type = userDefinedWidthId

    def draw(self):
        results = self.sketch.draw_finger()
        profiles = ObjectCollection.create()
        profiles.add(results[0])
        finger = self._extrude_finger(self.params.depth.value, profiles)

    def complete_draw(self, profiles):
        pass

    def extrude(self):
        # length = self.length - abs(tc.margin.value)*2
        # default_finger_count = max(3,
        #                        (math.ceil(math.floor(length / tc.default_width.value)/2)*2)-1)
        # if tc.start_with_tab:
        #     default_tab_count = math.ceil(default_finger_count/2)
        #     default_notch_count = default_tab_count - 1
        #     tab_length = tc.default_width.value * default_finger_count - tc.default_width.value*2
        # else:
        #     default_notch_count = math.ceil(default_finger_count/2) - 2
        #     default_tab_count = default_notch_count - 1
        #     tab_length = tc.default_width.value * default_finger_count

        # tab_length = tc.default_width.value * default_finger_count + tc.default_width.value
        # margin = (self.length - tab_length + tc.default_width.value) / 2
        # default_width = tc.default_width.value

        # if tc.start_with_tab is True:
        #     distance = length - margin*2 - default_width
        #     extrude_count = default_tab_count
        # else:
        #     distance = length - margin*2 - default_width*3
        #     extrude_count = default_tab_count - 1

        # tab_width = tc.default_width.value

        # params = FingerParams(tc.finger_type,
        #                       tc.start_with_tab,
        #                       tc.edge,
        #                       default_finger_count,
        #                       tc.length,
        #                       tc.default_width,
        #                       tab_width,
        #                       tc.depth,
        #                       tc.margin,
        #                       extrude_count,
        #                       tc.distance,
        #                       distance + abs(tc.margin.value)*2,
        #                       margin,
        #                       tc.parametric)
        # sketch = FingerSketch.create(tc.finger_type, self, params)

        # We need to save some information for future reference,
        # since the underlying data will change once any changes are
        # made to the associated BRepFace

        # We save the top_line of the sketch to use as a reference
        # for the rectangularPattern axis 1, and then find the
        # perpendicular edge that attaches to the top right point
        # of the sketch to use as a reference for axis 2
        tc = self._config

        # join_point = self.sketch.reference_points
        # primary_axis = self.sketch.reference_line.sketch_line
        # secondary_axis, secondary_point = self.perpendicular_edge_from_point(join_point)

        # profiles = self.sketch.draw_finger()
        # # pattern_params = FingerPattern(params.distance,
        # #                                tc.distance,
        # #                                params.notches,
        # #                                params.depth,
        # #                                params.offset)

        # profs = ObjectCollection.create()
        # finger_idx = 1 if tc.start_with_tab and len(profiles) > 1 else 2
        # profs.add(profiles[finger_idx])

        # if len(profiles) > 0:
        #     finger = self._extrude_finger(tc.depth, profs, self.sketch.params)
        #     self._duplicate_fingers(finger, primary_axis,
        #                             secondary_axis, tc.edge)
        #     profs.clear()

        #     if not tc.start_with_tab:
        #         profs.add(profiles[0])
        #         profs.add(profiles[4])
        #         corners = self._extrude_finger(tc.depth, profs, self.sketch.params)

        #         if tc.edge is not None:
        #             corner_params = FingerPattern(params.distance, tc.distance,
        #                                           params.notches, params.depth, params.offset)
        #             other_face = parallel_face(self.body.faces, self.sketch.reference_plane, secondary_point)
        #             newpoints = (secondary_point, None)
        #             corner_axis, spoint = self.perpendicular_edge_from_point(newpoints, face=other_face)
        #             if corner_axis:
        #                 self._duplicate_corners(corner_params, corners,
        #                                         corner_axis, tc.edge, self.sketch)

        #     if self._timeline and self._timeline.isValid:
        #         mp = self._timeline.markerPosition
        #         tcount = self._timeline.count - 1
        #         pos = mp if mp <= tcount else tcount
        #         tloffset = 2 if tc.start_with_tab else 4
        #         tlgroup = self._timeline.timelineGroups.add(pos-tloffset, pos)
        #         if self.sketch.params:
        #             tlgroup.name = '{} Finger Group'.format(self.sketch.params.name)

    def _duplicate_corners(self, params, feature, primary, secondary,
                           sketch=None):

        parameters = sketch.params
        quantity = createByReal(2)

        inputEntities = ObjectCollection.create()
        inputEntities.add(feature)

        parallel_distance = createByString('-({})'.format(parameters.distance_two.name))

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
            ui.messageBox(traceback.format_exc())

