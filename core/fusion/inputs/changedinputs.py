from ..face import dimensions
from ..face import distance_between
from ..face import distance_between_faces

from .inputreader import InputReader


class ChangedInputs(InputReader):

    def find_opposite(self):
        if self.face_selected and not self.single_edge_selected:
            plane = self.selected_face.geometry
            body = self.selected_face.body
            for alternate in body.faces:
                alternate_plane = alternate.geometry
                if alternate_plane.isParallelToPlane(plane):
                    if alternate.area == self.selected_face.area:
                        self.edge.addSelection(alternate)
        elif self.single_edge_selected:
            self.edge.clearSelection()

    def finger_placement(self):
        self.distance.isVisible = not self.single_edge_selected
        self.edge.isVisible = not self.single_edge_selected
        self.edge.isEnabled = not self.single_edge_selected

        if self.single_edge_selected:
            self.edge.clearSelection()
            self.face.hasFocus = self.edge.hasFocus

    def update_inputs(self):
        self.edge.hasFocus = self.face_selected and not self.edge_selected
        self.length.value = self.length_value
        self.distance.value = self.distance_value

    @property
    def length_value(self):
        if not self.selected_face:
            return 0

        return dimensions(self.selected_face).length

    @property
    def distance_value(self):
        if not self.face_selected or not self.edge_selected:
            return 0

        return distance_between_faces(self.selected_face,
                                      self.selected_edge)
