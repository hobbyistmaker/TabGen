# from .sketch import Sketch


class Body:

    @classmethod
    def from_face(cls, brepface):
        return cls(brepface.body)

    def __init__(self, brepbody):
        self.brepbody = brepbody
        self.edge_faces = sorted(self.faces, key=lambda face: face.area)[:-2]

        self.token = self.brepbody.attributes.itemByName('tabgen', 'tabbed_faces')
        if not self.token:
            self.token = self.brepbody.attributes.add('tabgen', 'tabbed_faces', str(0))

        self.patterns = self.parent.features.rectangularPatternFeatures
        self.extrudes = self.parent.features.extrudeFeatures

    def __getattr__(self, name, default):
        return getattr(self.brepbody, name, default)

    @property
    def current_face_id(self):
        return self.fc.value

    @property
    def next_face_id(self):
        return int(self.token.value) + 1

    def add_face(self, brepface):
        self.token.value = str(self.next_face_id)
        face_id = brepface.attributes.itemByName('tabgen', 'face_id')
        if not face_id:
            face_id = brepface.attributes.add('tabgen', 'face_id', self.token.value)
        else:
            face_id.value = self.token.value
        return int(self.token.value)

    def edge_by_sketch_point(self, point):
        for edge in self.edges:
            if point in (edge.startVertex, edge.endVertex):
                return edge
