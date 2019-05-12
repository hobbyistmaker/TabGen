import traceback

from adsk.core import Application
from adsk.core import ObjectCollection
from adsk.core import Plane
from adsk.core import Line3D
from adsk.core import ValueInput
from adsk.fusion import Design
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType

from ...util import d
from ...util import automaticWidthId
from ..fingersketch import FingerSketch

app = Application.get()
ui = app.userInterface

# some function aliases
CFO = FeatureOperations.CutFeatureOperation
EDT = PatternDistanceType.ExtentPatternDistanceType
createByReal = ValueInput.createByReal
createByString = ValueInput.createByString


def edge_matches_points(edge, point1, point2):
    """ Find the face edge that matches the associated points.

        This can find the face edge that matches two points from
        a sketch line.
        """
    edge_start = edge.startVertex.geometry
    edge_end = edge.endVertex.geometry

    if ((edge_start.isEqualTo(point1) and edge_end.isEqualTo(point2)) or
       (edge_start.isEqualTo(point2) and edge_end.isEqualTo(point1))):
        return True
    return False


class FingerFace:

    finger_type = automaticWidthId

    @classmethod
    def create(cls, manager, config):
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == config.finger_type]
        return (sc[0](manager, config)
                if len(sc) > 0
                else FingerFace(manager, config))

    def __init__(self, manager, config):
        design = Design.cast(app.activeProduct)
        try:
            self.__config = config
            self.__bface = config.face
            self.__manager = manager

            self.__prefix = self.name

            self.__face_count = config.face_id
        except:
            ui.messageBox(traceback.format_exc())

    def create_fingers(self):
        if self.bface.isValid and self._config is not None:
            self.sketch = FingerSketch.create(self, self._config)

            self.join_point = self.sketch.reference_points
            self.primary_axis = self.sketch.reference_line.sketch_line
            self.secondary_axis, self.secondary_point = self.perpendicular_edge_from_point(self.join_point)

            setup = self.__setup_draw()
            profiles = self.__draw(setup)
            complete = self.__complete_draw(profiles)
            self.__fix_timeline(complete)

        if self.face_count:
            value = int(self.face_count.value)
            self.face_count.value = str(value+1)
        else:
            self.face_count = self.body.attributes.add('tabgen', 'faces', str(1))

    def distance_to(self, second_face):
        """ For the edge selected by the user, find the
            minimum distance between the edge and this
            face. This minimum distance will be used
            for the calculation that defines how far
            to cut the fingers on the secondary face.
            """
        primary_face = Plane.cast(self.bface.geometry)
        this_face = Line3D.cast(second_face.geometry)

        distance = 0

        if primary_face.isParallelToLine(this_face):
            this_vertices = [second_face.startVertex.geometry,
                             second_face.endVertex.geometry]

            for primary_vertex in self.vertices:
                for second_vertex in this_vertices:
                    measure = d(primary_vertex, second_vertex)
                    if distance == 0 or measure < distance:
                        distance = measure
        return distance

    def edge_from_point(self, point, edge, reverse=False):
        """ Given a reference Point3D, return the vertex that
            matches.
            """
        if point.isEqualTo(edge.startVertex.geometry):
            return edge.endVertex if reverse else edge.startVertex
        if point.isEqualTo(edge.endVertex.geometry):
            return edge.startVertex if reverse else edge.endVertex

    def perpendicular_edge_from_point(self, points, face=None):
        """ Find the edge that is perpendicular to the
            upper right sketch point, for the secondary
            axis used in the rectangularPattern
            """
        point, other = points

        if face and not face.isValid:
            ui.messageBox('Face is invalid.')

        if face is None:
            plane = Plane.cast(self.__bface.geometry)
            edges = self._edges
        else:
            plane = Plane.cast(face.geometry)
            edges = face.edges

        # Loop through the edges of the face.
        # We want to find edges that connect to the reference point ("point")
        for edge in edges:
            if other is not None:
                if edge_matches_points(edge, point, other):
                    # start the loop over if this edge matches the sketch
                    # line. This is not the line that we want to use
                    continue

            # given an edge that doesn't match the sketch line,
            # get the point of the edge at the other side. restart
            # the loop if there's no match for some reason.
            connected = self.edge_from_point(point, edge)
            if not connected:
                continue

            for j in range(0, connected.edges.count):
                vedge = connected.edges.item(j)
                line = Line3D.cast(vedge.geometry)
                if plane.isPerpendicularToLine(line):
                    vother = self.edge_from_point(connected.geometry, vedge, reverse=True)
                    return (vedge, vother.geometry)
        return (None, None)

    def _extrude_finger(self, depth, profs):
        # Define the extrusion extent to be -tabDepth.
        extCutInput = self.extrudes.createInput(profs, CFO)
        # dist = createByString(str(-(depth.value*10)))
        dist = createByString(str(-abs(depth.value*10)))
        extCutInput.setDistanceExtent(False, dist)

        # Make sure that we only cut the body associated with this
        # face.
        extCutInput.participantBodies = [self.body]
        finger = self.extrudes.add(extCutInput)

        # Manually set the extrude expression -- for some reason
        # F360 takes the value of a ValueInput.createByString
        # instead of the expression
        self.params.depth.entity = finger.extentOne.distance
        finger.name = '{} Extrude'.format(self.name)
        # if parameters is not None:
        #     finger.extentOne.distance.expression = '-{}'.format(parameters.depth.name)

        return finger

    def _duplicate_fingers(self, finger, primary,
                           secondary, edge=None):

        params = self.sketch.params
        patterns = self.patterns

        ui.messageBox(params.notches.expression)
        ui.messageBox(params.cut_distance.expression)
        quantity = createByString(params.notches.expression)
        distance = createByString(params.cut_distance.expression)

        inputEntities = ObjectCollection.create()
        inputEntities.add(finger)

        patternInput = patterns.createInput(inputEntities,
                                            primary,
                                            quantity,
                                            distance,
                                            EDT)

        if edge is not None and secondary is not None:
            parallel_distance = createByString(params.distance_two.name)
            patternInput.setDirectionTwo(secondary,
                                         createByReal(2),
                                         parallel_distance)

        try:
            patternInput.patternComputeOption = 1
            pattern = patterns.add(patternInput)
            pattern.name = '{} Rectangle Pattern'.format(params.name)
            return pattern
        except:
            ui.messageBox(traceback.format_exc())

    def _draw(self, setup):
        self.sketch.draw_finger()

    def _setup_draw(self):
        pass

    def _complete_draw(self, profiles):
        pass

    def _fix_timeline(self, completion):
        pass

    __draw = _draw
    __setup_draw = _setup_draw
    __complete_draw = _complete_draw
    __fix_timeline = _fix_timeline

    @property
    def _config(self):
        return self.__config

    @property
    def _edges(self):
        return self.__edges

    @property
    def _prefix(self):
        return self.__prefix

    @property
    def bface(self):
        return self.__bface

    @property
    def body(self):
        return self.__bface.body

    @property
    def evaluator(self):
        return self.__bface.evaluator

    @property
    def extrudes(self):
        return self.parent.features.extrudeFeatures

    @property
    def face_count(self):
        if self.__face_count:
            return int(attribute.value) + 1
        return 1

    @property
    def is_edge(self):
        # Get the area for each face, remove the two largest,
        # and check if the current face is in the remaining list
        return self.__is_edge

    @property
    def length(self):
        return self.__length

    @property
    def mirrors(self):
        return self.parent.features.mirrorFeatures

    @property
    def name(self):
        return self.__bface.body.name

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
    def sketch(self):
        return self.__sketch

    @sketch.setter
    def sketch(self, sketch):
        self.__sketch = sketch

    @property
    def vertical(self):
        if self.__xlen == self.__width:
            return True
        return False

    @property
    def vertices(self):
        return self.__vertices

    @property
    def width(self):
        return self.__width

    @property
    def x_length(self):
        return self.__xlen

    @property
    def y_length(self):
        return self.__ylen
