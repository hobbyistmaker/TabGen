from ..base import Base

from .sketch import Sketch


class Body(Base):

    @classmethod
    def from_face(cls, brepface):
        return cls(brepface.body)

    def __init__(self, brepbody):
        super().__init__()

        self.brepbody = brepbody
        self.edge_faces = sorted(self.faces, key=lambda face: face.area)[:-2]
        self.fc = self.brepbody.attributes.itemByName('tabgen', 'faces')
        if not self.fc:
            self.fc = self.brepbody.attributes.add('tabgen', 'faces', str(0))

    def add_face(self):
        self.fc.value = str(int(self.fc.value) + 1)
        return self.fc.value

    def add_sketch(self, name, face):
        return Sketch(name, self, face)

    def edge_by_sketch_point(self, point):
        for edge in self.edges:
            if point in (edge.startVertex, edge.endVertex):
                return edge

    def is_edge(self, face):
        return face in self.edge_faces

    @property
    def edges(self):
        return self.brepbody.edges

    @property
    def extrudes(self):
        return self.parent.features.extrudeFeatures

    @property
    def faces(self):
        return self.brepbody.faces

    @property
    def current_face_id(self):
        return self.fc.value

    @property
    def name(self):
        return self.brepbody.name

    @property
    def parent(self):
        return self.brepbody.parentComponent

    @property
    def patterns(self):
        return self.parent.features.rectangularPatternFeatures
