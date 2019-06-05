from ... import definitions as defs

from ... import managers

create_properties = {
    defs.automaticWidthId: managers.create_auto_width,
    defs.userDefinedWidthId: managers.create_constant_width,
    defs.constantCountId: managers.create_constant_count
}

class InputReader:

    def __init__(self, inputs, preview=False):
        self.placement = inputs.itemById(defs.fingerPlaceId).selectedItem.name
        self.face = inputs.itemById(defs.selectedFaceInputId)
        self.edge = inputs.itemById(defs.dualEdgeSelectId)
        self.reference_edges = inputs.itemById(defs.referenceSelectId)
        self.length = inputs.itemById(defs.lengthInputId)
        self.distance = inputs.itemById(defs.distanceInputId)
        self.depth = inputs.itemById(defs.mtlThickInputId)
        self.margin = inputs.itemById(defs.marginInputId)
        self.width = inputs.itemById(defs.tabWidthInputId)
        self.kerf = inputs.itemById(defs.kerfInputId)
        self.interior = inputs.itemById(defs.wallCountInputId)
        self.tab_first = inputs.itemById(defs.startWithTabInputId).value
        self.finger_type = inputs.itemById(defs.fingerTypeId).selectedItem.name
        self.parametric = inputs.itemById(defs.parametricInputId).value
        self.preview_enabled = inputs.itemById(defs.previewInputId).value
        self.err = inputs.itemById(defs.ERROR_MSG_INPUT_ID)
        self.preview = preview

        self.face_selected = self.face.selectionCount > 0
        self.selected_face = self.face.selection(0).entity if self.face_selected else None

        self.selected_body = self.selected_face.body if self.selected_face else None

        self.edge_selected = self.edge.selectionCount > 0
        self.selected_edge = self.edge.selection(0).entity if self.edge_selected else None

    @property
    def name(self):
        return self.selected_body.name

    @property
    def dual_edge_selected(self):
        return not self.single_edge_selected

    @property
    def single_edge_selected(self):
        return self.placement == defs.singleEdgeId

    def alternate_edge(self, edge):
        if not self.face_selected:
            return True

        return edge not in self.selected_face.edges

    def alternate_face(self, face):
        if not self.edge_selected:
            return True

        return self.selected_edge not in face.edges

    def face_parallel_to_edge(self, edge):
        if not self.face_selected:
            return True

        return self.selected_face.geometry.isParallelToPlane(edge.geometry)

    def edge_parallel_to_face(self, face):
        if not self.edge_selected:
            return True

        return face.geometry.isParallelToPlane(self.selected_edge.geometry)

    def opposite_face(self, face):
        if self.edge_selected and self.face_selected:
            return False

        if self.face_selected:
            if (self.selected_face == face) or (not face.geometry.isParallelToPlane(self.selected_face.geometry)):
                return False
            return face.area == self.selected_face.area
        elif self.edge_selected:
            if (self.selected_edge == face) or (not face.geometry.isParallelToPlane(self.selected_edge.geometry)):
                return False
            return face.area == self.selected_edge.area

        return True

    def create_properties(self, app, ui):
        return create_properties[self.finger_type](app, ui, self)