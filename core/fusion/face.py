import traceback

from collections import namedtuple

from adsk.core import Plane
from adsk.core import Line3D

from ..base import Base
from .body import Body
from .sketch import Sketch


Axis = namedtuple('Axis', ['name', 'value'])
Dimensions = namedtuple('Dimensions', ['width', 'length'])
PerpendicularEdge = namedtuple('PerpendicularEdge', ['join_point', 'edge', 'other_point'])


class Face(Base):

    @classmethod
    def from_inputs(cls, config):
        try:
            return cls(config.brepface, config)
        except:
            cls.trace('Failed creating Face object')

    @classmethod
    def from_entity(cls, value):
        try:
            return cls(value)
        except:
            cls.trace('Failed creating Face object')

    @classmethod
    def dimensions(cls, brepface):
        evaluator = brepface.evaluator
        prange = evaluator.parametricRange()

        x_length = prange.maxPoint.x - prange.minPoint.x
        y_length = prange.maxPoint.y - prange.minPoint.y

        width = min(x_length, y_length)
        length = max(x_length, y_length)

        return Dimensions(width, length)

    @classmethod
    def distance_between(cls, face, edge):
        """ For the edge selected by the user, find the
            minimum distance between the edge and this
            face. This minimum distance will be used
            for the calculation that defines how far
            to cut the fingers on the secondary face.
            """
        try:
            plane = face.as_plane

            distance = 0

            if plane.isParallelToLine(edge.geometry):
                this_vertices = [edge.startVertex.geometry,
                                 edge.endVertex.geometry]

                for primary_vertex in face.vertices:
                    for second_vertex in this_vertices:
                        measure = face.distance(primary_vertex.geometry, second_vertex)
                        if distance == 0 or measure < distance:
                            distance = measure
            return distance
        except:
            cls.trace('Failed getting distance between faces')

        return 0

    @classmethod
    def perpendicular_edge_from_vertex(cls, face, vertex):
        """ From a given vertex on the face, find the
            perpendicular edge on a connected face.
            """
        connected = vertex.edges

        other = connected[0].startVertex
        edge = None

        for testedge in connected:
            line = Line3D.cast(testedge.geometry)
            if face.as_plane.isPerpendicularToLine(line):
                edge = testedge
                start = testedge.startVertex
                end = testedge.endVertex
                if start == vertex:
                    other = end

        return PerpendicularEdge(vertex, edge, other)

    @classmethod
    def set_face_orientation(cls, face):
        """ Make a basic attempt to determine the major axis orientation
            to make naming of created sketches and features somewhat
            useful.
            """
        uvector = face.as_plane.uDirection.copy()
        vvector = face.as_plane.vDirection.copy()

        uvector.normalize()
        vvector.normalize()

        combined = ((uvector.x + vvector.x)/2, (uvector.y + vvector.y)/2, (uvector.z + vvector.z)/2)

        axes = []
        if combined[0] != 0:
            axes.append(Axis('X', combined[0]))
        if combined[1] != 0:
            axes.append(Axis('Y', combined[1]))
        if combined[2] != 0:
            axes.append(Axis('Z', combined[2]))

        axes = sorted(axes, key=lambda key: key.value)
        count = len(axes)

        resultx = '{}'.format(axes[0].name) if count > 0 else ''
        resulty = resultx + '{}'.format(axes[1].name) if count > 1 else ''
        resultz = resulty + '{}'.format(axes[2].name) if count > 2 else ''

        return resultz

    def __init__(self, brepface, config=None):
        super().__init__()

        self.brepface = brepface

        self.body = Body.from_face(self.brepface)
        self.config = config

        self.orientation = self.set_orientation()
        self.fc = self.brepface.attributes.itemByName('tabgen', 'face_id')

        self.width, self.length = self.dimensions(self.brepface)

        self.edges = self.brepface.edges
        self.vertices = self.brepface.vertices

    def add_sketch(self):
        """ Create a sketch using this face as the reference.
        """
        if not self.fc:
            self.fc = self.brepface.attributes.add('tabgen', 'faces', self.body.add_face())

        name = '{name}{idx} Finger Sketch'.format(name=self.name,
                                                  idx=self.fc.value)
        sketch = self.body.add_sketch(name, self)
        return sketch

    def distance_to(self, second_face):
        return self.distance_between(self, second_face)

    def edge_on_face(self, edge):
        """ Checks if a given edge is on this face.
        """
        return edge in self.edges

    def isParallelToLine(self, edge):
        """ Checks if a given edge is parallel to this
            face.
            """
        try:
            if not self.edge_on_face(edge):
                line = Line3D.cast(edge.geometry)
                return self.as_plane.isParallelToLine(line)
            else:
                return False
        except:
            self.trace('Failed comparing edge to face')

    def perpendicular_from_vertex(self, vertex):
        return self.perpendicular_edge_from_vertex(self, vertex)

    def set_orientation(self):
        return self.set_face_orientation(self)

    def mark_complete(self):
        self.brepface.attributes.add('tabgen', 'completed', str(1))

    @property
    def is_completed(self):
        return self.brepface.attributes.itemByName('tabgen', 'completed')

    @property
    def as_plane(self):
        """ Returns this face as a Plane.
        """
        return Plane.cast(self.brepface.geometry)

    @property
    def extrudes(self):
        return self.body.extrudes

    @property
    def geometry(self):
        return self.brepface.geometry

    @property
    def is_edge(self):
        """ Checks to see if this face is an "edge"
            of the parent body.
            """
        if self.body:
            return self.body.is_edge(self.brepface)
        else:
            return False

    @property
    def name(self):
        if self.fc:
            fc = self.fc.value
        else:
            fc = int(self.body.fc.value) + 1
        return '{body} {orientation}{face_num}'.format(body=self.body.name,
                                                       orientation=self.orientation,
                                                       face_num=fc)

    @property
    def alias(self):
        return self.clean_string(self.name)

    @property
    def patterns(self):
        return self.body.patterns
