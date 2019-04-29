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
from ...util import uimessage

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

    finger_type = 'none'

    @classmethod
    def create(cls, fingertype, entity, params=None):
        sc = [subclass for subclass in cls.__subclasses__()
              if subclass.finger_type == fingertype]
        return (sc[0](entity, params)
                if len(sc) > 0
                else FingerFace(entity, params))

    def __init__(self, bface, params=None, pface=None):
        design = Design.cast(app.activeProduct)

        self._ui = ui
        self.__bface = bface
        self.__evaluator = bface.geometry.evaluator
        pRange = self.evaluator.parametricRange()

        self.__xlen = pRange.maxPoint.x - pRange.minPoint.x
        self.__ylen = pRange.maxPoint.y - pRange.minPoint.y

        self.__vertices = [bface.vertices.item(j).geometry
                           for j in range(bface.vertices.count)]

        self.__width = min(self.__xlen, self.__ylen)
        self.__length = max(self.__xlen, self.__ylen)

        self.__tab_params = params

        self.__xy = False
        self.__xz = False
        self.__yz = False
        self._timeline = design.timeline

        self._edges = [self.body.edges.item(j)
                       for j in range(0, self.body.edges.count)]

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

            # if face is not None:
            #     ui.messageBox('Checking edge.')
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

    def distance_to(self, second_face):
        """ For the edge selected by the user, find the
            minimum distance between the edge and this
            face. This minimum distance will be used
            for the calculation that defines how far
            to cut the fingers on the secondary face.
            """
        primary_face = Plane.cast(self.__bface.geometry)
        this_face = Line3D.cast(second_face.geometry)

        distance = 0

        if primary_face.isParallelToLine(this_face):
            this_vertices = [second_face.startVertex.geometry,
                             second_face.endVertex.geometry]

            for primary_vertex in self.__vertices:
                for second_vertex in this_vertices:
                    measure = d(primary_vertex, second_vertex)
                    if distance == 0 or measure < distance:
                        distance = measure
        return distance

    @property
    def face_count(self):
        attribute = self.body.attributes.itemByName('tabgen', 'faces')
        if attribute:
            return int(attribute.value) + 1
        return 1

    def _extrude_finger(self, depth, profs, parameters=None):
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
        if parameters is not None:
            finger.name = '{} Extrude'.format(parameters.name)
            finger.extentOne.distance.expression = '-{}'.format(parameters.fingerd.name)

        return finger

    def _duplicate_fingers(self, params, finger, primary,
                           secondary, edge=None, sketch=None):

        parameters = sketch.parameters
        dov = -params.distance

        if parameters is None:
            quantity = createByReal(params.notches)
            distance = createByReal(dov)
        else:
            quantity = createByString(parameters.extrude_count.name)
            distance = createByString(parameters.fdistance.name)

        inputEntities = ObjectCollection.create()
        inputEntities.add(finger)

        patternInput = self.patterns.createInput(inputEntities,
                                                 primary,
                                                 quantity,
                                                 distance,
                                                 EDT)

        if edge is not None and secondary is not None:
            sdistance = abs(params.distance_two.value)

            if parameters is not None:
                # parameters.add_far_length(sdistance)
                parallel_distance = createByString(parameters.distance_two.name)
            else:
                parallel_distance = createByReal(sdistance - params.depth.value)

            patternInput.setDirectionTwo(secondary,
                                         createByReal(2),
                                         parallel_distance)

        try:
            patternInput.patternComputeOption = 1
            pattern = self.patterns.add(patternInput)
            if parameters is not None:
                pattern.name = '{} Rectangle Pattern'.format(parameters.name)
            return pattern
        except:
            uimessage(traceback.format_exc())

    def extrude(self, tc):
        pass

    __extrude = extrude

    def create_fingers(self):
        if self.bface.isValid and self.__tab_params is not None:
            self.extrude(self.__tab_params)

        self.__faces = self.body.attributes.itemByName('tabgen', 'faces')
        if self.__faces:
            value = int(self.__faces.value)
            self.__faces.value = str(value+1)
        else:
            self.__faces = self.body.attributes.add('tabgen', 'faces', str(1))

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
    def evaluator(self):
        return self.__bface.evaluator

    @property
    def extrudes(self):
        return self.parent.features.extrudeFeatures

    @property
    def is_edge(self):
        # Get the area for each face, remove the two largest,
        # and check if the current face is in the remaining list
        faces = sorted([self.body.faces.item(j)
                        for j in range(0, self.body.faces.count)],
                       key=lambda face: face.area)
        return self.__bface in faces[:-2]


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
