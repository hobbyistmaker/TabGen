import itertools
import traceback

from collections import namedtuple

from adsk.core import Plane
from adsk.core import Line3D

from ..body import Body
from .dimensions import dimensions
from .sketch import Sketch
from .util import clean_string
from .util import distance
from .util import trim_zeros


class Face:

    @classmethod
    def from_inputs(cls, app, ui, config):
        return cls(app, ui, config.selected_face, config)

    def __init__(self, app, ui, brepface, config):
        self.app = app
        self.ui = ui
        self.brepface = brepface
        self.plane = self.brepface.geometry

        self.body = Body.from_face(self.brepface)
        self.config = config

        self.orientation = face_orientation(self.brepface)
        self.fc = self.face_id

        self.width, self.length = dimensions(self.brepface)

        self.is_completed = self.brepface.attributes.itemByName('tabgen', 'completed')
        self.alias = clean_string(self.name)

    def __getattr__(self, name, default):
        return getattr(self.brepface, name, default)

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
        return distance_between(self.brepface, second_face)

    def edge_on_face(self, edge):
        """ Checks if a given edge is on this face.
        """
        return edge_on_face(self.brepface, edge)

    def isParallelToLine(self, edge):
        """ Checks if a given edge is parallel to this
            face.
            """
        return parallel_to_edge(self.brepface, edge)

    def perpendicular_from_vertex(self, vertex):
        return perpendicular_edge_from_vertex(self, vertex)

    def mark_complete(self):
        self.brepface.attributes.add('tabgen', 'completed', str(1))

    @property
    def is_edge(self):
        """ Checks to see if this face is an "edge"
            of the parent body.
            """
        return self.body.is_edge(self.brepface)

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
    def face_id(self):
        fid = self.brepface.attributes.itemByName('tabgen', 'face_id')
        if not fid:
            return self.body.next_face_id
        return fid
