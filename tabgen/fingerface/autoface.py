import math

from adsk.core import Application
from adsk.core import ObjectCollection
from adsk.core import ValueInput
from adsk.fusion import Design
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType

from ...util import automaticWidthId
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


class AutoFace(FingerFace):

    finger_type = automaticWidthId

    def extrude(self):
        def small_tabs():
            return True if tc.default_width.value < tc.depth.value*2 else False

        tc = self._config
        # Calculate the parameters that will be used to define the spacing,
        # size and distance of the notches that will be cut in the face
        length = self.length-abs(tc.margin.value)*2

        default_finger_count = max(3,
                                   (math.ceil(math.floor(length / tc.default_width.value)/2)*2)-1)
        default_tab_width = length / default_finger_count
        default_notch_count = math.floor(default_finger_count/2)

        if tc.start_with_tab:
            extrude_count = default_notch_count
            distance = (default_finger_count - 3) * default_tab_width
            tab_width = default_tab_width
        else:
            extrude_count = default_finger_count - default_notch_count
            distance = (default_finger_count - 1) * default_tab_width
            tab_width = 0

        params = FingerParams(tc.finger_type,
                              tc.start_with_tab,
                              tc.edge,
                              default_finger_count,
                              tc.length,
                              tc.default_width,
                              default_tab_width,
                              tc.depth,
                              tc.margin,
                              extrude_count,
                              tc.distance,
                              distance,
                              tab_width,
                              tc.parametric)
        sketch = FingerSketch.create(tc.finger_type, self, params)
        self.body.attributes.add('Tabgen', 'sketch', sketch.sketch_alias)

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

        # Draw the rectangle that will be used to cut finger notches
        # in the face
        profiles = sketch.draw_finger()

        # Select the correct profile from the sketch to cut the notches
        profs = ObjectCollection.create()
        if tc.start_with_tab and len(profiles) > 1:
            profs.add(profiles[1])
        else:
            profs.add(profiles[0])

        # Cut the notches and duplicate them across the face--and, if selected
        # across a parallel face
        if len(profiles) > 0:
            pattern_params = FingerPattern(params.distance,
                                           tc.distance,
                                           params.notches,
                                           params.depth,
                                           params.offset)
            finger = self._extrude_finger(tc.depth, profs, sketch.parameters)
            self._duplicate_fingers(pattern_params, finger,
                                    primary_axis, secondary_axis,
                                    tc.edge, sketch)

            # If the timeline exists and is valid, group the last 3 operations
            # together on the timeline
            if self._timeline and self._timeline.isValid:
                mp = self._timeline.markerPosition
                tcount = self._timeline.count - 1
                lpos = mp if mp <= tcount else tcount
                spos = 0 if lpos < 2 else lpos-2
                tlgroup = self._timeline.timelineGroups.add(spos, lpos)
                if sketch.parameters:
                    tlgroup.name = '{} Finger Group'.format(sketch.parameters.name)
