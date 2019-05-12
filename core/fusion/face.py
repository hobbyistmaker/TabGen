import traceback

from collections import namedtuple

from adsk.core import Plane
from adsk.core import Line3D

from ..tabconfig import TabConfig
from ..base import Base
from .body import Body
from .sketch import Sketch


Axis = namedtuple('Axis', ['name', 'value'])
PerpendicularEdge = namedtuple('PerpendicularEdge', ['join_point', 'edge', 'other_point'])


class Face(Base):

    @classmethod
    def from_inputs(cls, inputs):
        try:
            config = TabConfig(inputs)
            return cls(config.face, config)
        except:
            cls.trace('Failed creating Face object')

    @classmethod
    def from_entity(cls, value):
        try:
            return cls(value)
        except:
            cls.trace('Failed creating Face object')

    def __init__(self, brepface, config=None):
        super().__init__()

        self.brepface = brepface

        self.body = Body.from_face(self.brepface)
        self.config = config

        self.orientation = self.set_orientation()

        evaluator = self.brepface.evaluator
        prange = evaluator.parametricRange()
        self.x_length = prange.maxPoint.x - prange.minPoint.x
        self.y_length = prange.maxPoint.y - prange.minPoint.y

        self.edges = self.brepface.edges

        self.width = min(self.x_length, self.y_length)
        self.length = max(self.x_length, self.y_length)

        self.vertices = self.brepface.vertices

    def add_sketch(self):
        """ Create a sketch using this face as the reference.
        """
        name = '{name}{idx} Finger Sketch'.format(name=self.name,
                                                  idx=self.body.add_face())
        sketch = self.body.add_sketch(name, self)
        return sketch

    def distance_to(self, second_face):
        """ For the edge selected by the user, find the
            minimum distance between the edge and this
            face. This minimum distance will be used
            for the calculation that defines how far
            to cut the fingers on the secondary face.
            """
        try:
            primary_face = self.as_plane
            this_face = Line3D.cast(second_face.geometry)

            distance = 0

            if primary_face.isParallelToLine(this_face):
                this_vertices = [second_face.startVertex.geometry,
                                 second_face.endVertex.geometry]

                for primary_vertex in self.vertices:
                    for second_vertex in this_vertices:
                        measure = self.distance(primary_vertex.geometry, second_vertex)
                        if distance == 0 or measure < distance:
                            distance = measure
            return distance
        except:
            self.trace('Failed getting distance between faces')

        return 0

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
        """ From a given vertex on the face, find the
            perpendicular edge on a connected face.
            """
        connected = vertex.edges

        other = connected.item(0).startVertex
        for j in range(0, connected.count):
            vedge = connected.item(j)
            line = Line3D.cast(vedge.geometry)
            if self.as_plane.isPerpendicularToLine(line):
                start = vedge.startVertex
                end = vedge.endVertex
                if start == vertex:
                    other = end

        return PerpendicularEdge(vertex, vedge, other)

    def set_orientation(self):
        """ Make a basic attempt to determine the major axis orientation
            to make naming of created sketches and features somewhat
            useful.
            """
        uvector = self.as_plane.uDirection.copy()
        vvector = self.as_plane.vDirection.copy()

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
        return '{body} {orientation}'.format(body=self.body.name,
                                             orientation=self.orientation)

    @property
    def patterns(self):
        return self.body.patterns
