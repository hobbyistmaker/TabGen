import math
import traceback

from collections import namedtuple

from adsk.core import Application
from adsk.core import ObjectCollection
from adsk.core import ValueInput
from adsk.fusion import Design
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType

from ..util import uimessage
from ..util import automaticWidthId, userDefinedWidthId
from .fingersketch import FingerSketch
from .fingeredge import FingerEdge

app = Application.get()
ui = app.userInterface
design = Design.cast(app.activeProduct)

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
createByReal = ValueInput.createByReal
createByString = ValueInput.createByString

FingerParams = namedtuple('FingerParams', ['finger_type',
                                           'start_with_tab',
                                           'edge',
                                           'fingers',
                                           'default_width',
                                           'width',
                                           'depth',
                                           'notches',
                                           'distance',
                                           'offset',
                                           'parametric'])
Point = namedtuple('Point', ['origin', 'xdir', 'ydir'])


class FingerFace:

    def __init__(self, bface, ui=None, pface=None):
        self.__ui = ui
        self.__bface = bface
        self.__evaluator = bface.geometry.evaluator
        pRange = self.evaluator.parametricRange()

        self.__xlen = pRange.maxPoint.x - pRange.minPoint.x
        self.__ylen = pRange.maxPoint.y - pRange.minPoint.y

        self.__vertices = [bface.vertices.item(j).geometry
                           for j in range(bface.vertices.count)]

        self.__width = min(self.__xlen, self.__ylen)
        self.__length = max(self.__xlen, self.__ylen)

        self.__xy = False
        self.__xz = False
        self.__yz = False
        self.__timeline = design.timeline

        self.__connected = []

    def __create_automatic(self, tc):
        default_finger_count = max(3,
                                   (math.ceil(math.floor(self.length / tc.default_width.value)/2)*2)-1)
        default_tab_width = self.length / default_finger_count
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
                              tc.default_width,
                              default_tab_width,
                              tc.depth,
                              extrude_count,
                              distance,
                              tab_width,
                              tc.parametric)
        sketch = FingerSketch(self, params, self.__ui)
        profiles = sketch.draw_finger()

        profs = ObjectCollection.create()
        profs.add(profiles[1])

        if len(profiles) > 0:
            finger = self.__extrude_finger(tc.depth, profs, sketch.parameters)
            pattern = self.__duplicate_fingers(params, finger, tc.edge, sketch.parameters)

            if self.__timeline and self.__timeline.isValid:
                mp = self.__timeline.markerPosition
                tcount = self.__timeline.count - 1
                pos = mp if mp <= tcount else tcount
                self.__timeline.timelineGroups.add(pos-2, pos)

    def __create_defined(self, tc):
        default_finger_count = int(self.length // tc.default_width.value)
        default_tab_count = int(self.length // (2 * tc.default_width.value))
        tab_length = 2 * tc.default_width.value * default_tab_count
        margin = (self.length - tab_length + tc.default_width.value) / 2
        distance = self.length - margin * 2 - tc.default_width.value
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
        sketch = FingerSketch(self, params, self.__ui)
        profiles = sketch.draw_finger()

        profs = ObjectCollection.create()
        if tc.start_with_tab and len(profiles) > 1:
            profs.add(profiles[1])
        else:
            profs.add(profiles[0])
            profs.add(profiles[4])
            self.__extrude_finger(tc.depth, profs, sketch.parameters)
            profs.clear()
            profs.add(profiles[2])

        if len(profiles) > 0:
            finger = self.__extrude_finger(tc.depth, profs, sketch.parameters)
            self.__duplicate_fingers(params, finger, tc.edge, sketch.parameters)

    def __extrude_finger(self, depth, profs, parameters=None):
        # Define the extrusion extent to be -tabDepth.
        d = createByString(str(-(depth.value*10)))

        # Cut the first notch.
        finger = self.extrudes.addSimple(profs, d, CFO)
        # Manually set the extrude expression -- for some reason
        # F360 takes the value of a ValueInput.createByString
        # instead of the expression
        if parameters is not None:
            finger.extentOne.distance.expression = parameters.fingerd.name
            finger.name = '{} Extrude'.format(parameters.name)

        return finger

    def __duplicate_fingers(self, params, finger, edge=None, parameters=None):
        if parameters is None:
            quantity = createByReal(params.notches)
            distance = createByReal(params.distance)
        else:
            quantity = createByString(parameters.extrude_count.name)
            distance = createByString(parameters.fdistance.name)

        inputEntities = ObjectCollection.create()
        inputEntities.add(finger)

        patternInput = self.patterns.createInput(inputEntities,
                                                 self.parent.xConstructionAxis,
                                                 quantity,
                                                 distance,
                                                 EDT)
        patternInput.directionOneEntity = self.axis

        if edge is not None:
            selected = FingerEdge(edge)
            sdistance = selected.distance(self.__vertices, params.depth.value)

            if parameters is not None:
                parameters.add_far_length(selected.distance(self.__vertices))
                parallel_distance = createByString(parameters.distance_two.name)
            else:
                parallel_distance = createByReal(sdistance)

            patternInput.setDirectionTwo(self.__find_secondary_axis,
                                         createByReal(2),
                                         parallel_distance)

        try:
            pattern = self.patterns.add(patternInput)
            if parameters is not None:
                pattern.name = '{} Rectangle Pattern'.format(parameters.name)
            return pattern
        except:
            uimessage(self.__ui, traceback.format_exc(1))

    def __find_primary_axis(self):
        def check_axis(xlen, ylen, zlen, xaxis, yaxis, zaxis):
            if xaxis and yaxis:
                self.__xy = True
                if xlen == self.__width:
                    return self.parent.yConstructionAxis
                else:
                    return self.parent.xConstructionAxis

            elif xaxis and zaxis:
                self.__xz = True

                if xlen == self.__width:
                    return self.parent.zConstructionAxis
                else:
                    return self.parent.xConstructionAxis

            elif yaxis and zaxis:
                self.__yz = True

                if ylen == self.__width:
                    return self.parent.zConstructionAxis
                else:
                    return self.parent.yConstructionAxis

        return self.__scan_vertices(check_axis)

    def __scan_vertices(self, func):
        if self.__vertices:
            xlen, ylen, zlen = (0, 0, 0)
            xaxis, yaxis, zaxis = (0, 0, 0)
            xmax, ymax, zmax = (0, 0, 0)
            xmin, ymin, zmin = (0, 0, 0)

            point = self.__vertices[0]
            for vertex in self.__vertices:
                xaxis = 0 if (vertex.x == point.x) and not xaxis else 1
                yaxis = 0 if (vertex.y == point.y) and not yaxis else 1
                zaxis = 0 if (vertex.z == point.z) and not zaxis else 1

                xlen = max(xlen, vertex.x)
                ylen = max(ylen, vertex.y)
                zlen = max(zlen, vertex.z)

                xmax = max(xmax, vertex.x)
                xmin = min(xmin, vertex.x)
                ymax = max(ymax, vertex.y)
                ymin = min(ymin, vertex.y)
                zmax = max(zmax, vertex.z)
                zmin = min(zmin, vertex.z)

            return func(xlen, ylen, zlen, xaxis, yaxis, zaxis)

    @property
    def __find_secondary_axis(self):
        def check_axis(xlen, ylen, zlen, xaxis, yaxis, zaxis):
            if xaxis and yaxis:
                return self.parent.zConstructionAxis

            elif xaxis and zaxis:
                return self.parent.yConstructionAxis

            elif yaxis and zaxis:
                return self.parent.xConstructionAxis

        return self.__scan_vertices(check_axis)

    def create_fingers(self, tab_config):
        # hide other bodies to prevent accidental cuts
        bodies = self.parent.bRepBodies
        for j in range(0, bodies.count):
            body = bodies.item(j)
            body.isVisible = False
        bodies.itemByName(self.name).isVisible = True

        if self.bface.isValid:
            funcs = {
                automaticWidthId: self.__create_automatic,
                userDefinedWidthId: self.__create_defined
            }

            # if tab_config.parametric:
            #     check_param('{}_dfingerw'.format(clean_param(self.name)),
            #                 tab_config.default_width)

            func = funcs[tab_config.finger_type]
            func(tab_config)

        # show other bodies when finished
        # this should eventually track bodies that were visible before
        for j in range(0, bodies.count):
            body = bodies.item(j)
            body.isVisible = True

    @property
    def name(self):
        return self.__bface.body.name

    @property
    def axis(self):
        return self.__find_primary_axis()

    @property
    def bface(self):
        return self.__bface

    @property
    def body(self):
        return self.__bface.body

    @property
    def equal_faces(self):
        length = None
        for face in self.perpendicular_faces:
            length = face.length if length is None else length
            if length != face.length:
                return False
        return True

    @property
    def evaluator(self):
        return self.__bface.evaluator

    @property
    def extrudes(self):
        return self.parent.features.extrudeFeatures

    @property
    def is_edge(self):
        faces = self.body.faces
        for j in range(0, faces.count):
            face = FingerFace(faces.item(j), self.__ui)
            if face.width < self.width:
                return False

    @property
    def length(self):
        return self.__length

    @property
    def mirrors(self):
        return self.parent.features.mirrorFeatures

    @property
    def parent(self):
        return self.__bface.body.parentComponent

    @property
    def patterns(self):
        return self.parent.features.rectangularPatternFeatures

    @property
    def planes(self):
        return self.parent.constructionPlanes

    @property
    def vertical(self):
        if self.__xlen == self.__width:
            return True
        return False

    @property
    def width(self):
        return self.__width

    @property
    def x_length(self):
        return self.__xlen

    @property
    def xy(self):
        return self.__xy

    @property
    def xz(self):
        return self.__xz

    @property
    def y_length(self):
        return self.__ylen

    @property
    def yz(self):
        return self.__yz

    @property
    def vertices(self):
        return self.__vertices
