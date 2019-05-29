from ... import definitions as defs

class InputReader:

    def __init__(self, inputs):
        self.placement = inputs.itemById(defs.fingerPlaceId)
        self.face = inputs.itemById(defs.selectedFaceInputId)
        self.edge = inputs.itemById(defs.dualEdgeSelectId)
        self.length = inputs.itemById(defs.lengthInputId)
        self.distance = inputs.itemById(defs.distanceInputId)
        self.depth = inputs.itemById(defs.mtlThickInputId)
        self.margin = inputs.itemById(defs.marginInputId)
        self.width = inputs.itemById(defs.tabWidthInputId)
        self.interior = inputs.itemById(defs.wallCountInputId)
        self.repeat = inputs.itemById(defs.repeatInputId)
        self.tab_first = inputs.itemById(defs.startWithTabInputId).value
        self.finger_type = inputs.itemById(defs.fingerTypeId).selectedItem.name
        self.parametric = inputs.itemById(defs.parametricInputId).value
        self.err = inputs.itemById(defs.ERROR_MSG_INPUT_ID)

        self.face_selected = self.face and self.face.selectionCount > 0
        self.selected_face = self.face.selection(0).entity if self.face_selected else None
        self.selected_body = self.selected_face.body if self.selected_face else None
        self.edge_selected = self.edge and self.edge.selectionCount > 0
        self.selected_edge = self.edge.selection(0).entity if self.edge_selected else None
        self.single_edge_selected = self.placement.selectedItem.name == defs.singleEdgeId
        self.dual_edge_selected = not self.single_edge_selected

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

        return self.selected_face.geometry.isParallelToLine(edge.geometry)

    def edge_parallel_to_face(self, face):
        if not self.edge_selected:
            return True

        return face.geometry.isParallelToLine(self.selected_edge.geometry)

