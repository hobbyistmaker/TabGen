from ... import definitions as defs
from ..face import dimensions
from ..face import distance_between_faces

from .inputreader import InputReader


class ChangedInputs(InputReader):

    def update_finger_type(self):
        if self.finger_type == defs.constantCountId:
            self.width.isVisible = False
            self.width.isEnabled = False
            self.width.value = 0
            self.finger_count.value = 3
            self.finger_count.isEnabled = True
            self.finger_count.isVisible = True
        else:
            self.finger_count.isVisible = False
            self.finger_count.isEnabled = False
            self.finger_count.value = 3
            self.width.value = 1
            self.width.isEnabled = True
            self.width.isVisible = True

    def find_opposite(self):
        if self.face_selected and not self.single_edge_selected:
            plane = self.selected_face.geometry
            body = self.selected_face.body
            for alternate in body.faces:
                if alternate == self.selected_face:
                    continue
                alternate_plane = alternate.geometry
                if alternate_plane.isParallelToPlane(plane):
                    if round(alternate.area, 3) == round(self.selected_face.area, 3):
                        if self.edge.addSelection(alternate):
                            self.edge_selected = self.edge.selectionCount > 0
                            self.selected_edge = self.edge.selection(0).entity if self.edge_selected else None

    def finger_placement(self):
        if self.single_edge_selected:
            self.edge.clearSelection()
            self.face.hasFocus = self.edge.hasFocus
            self.edge.isEnabled = False
            self.edge.isVisible = False
            self.distance.isVisible = False
            self.distance.value = 0
            self.distance.isEnabled = False
        else:
            self.edge.isEnabled = True
            self.edge.isVisible = True
            self.distance.isVisible = True
            self.distance.isEnabled = True

    def update_inputs(self):
        if self.edge.isEnabled:
            self.edge.hasFocus = self.face_selected and not self.edge_selected

        self.length.value = self.length_value

        if self.distance.isEnabled:
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

        return distance_between_faces(self.app,
                                      self.selected_face,
                                      self.selected_edge)
