import adsk.core
import traceback

from ..util import d
from ..util import dualEdgeSelectId
from ..util import selectedFaceInputId
from ..util import uimessage

# Constants

eventFailedMsg = 'TabGen input changed event failed: {}'

tolerance = 0.001


class InputChangedHandler(adsk.core.InputChangedEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui

    def notify(self, args):
        try:
            cmdInput = args.input
            # If it is the selection input that got changed, check
            # that the selections are all a rectangles; deslelect
            # those that are not.
            if cmdInput.id == selectedFaceInputId:

                for i in range(cmdInput.selectionCount):
                    face = cmdInput.selection(i).entity
                    vertices = face.vertices
                    bad = True

                    if vertices.count == 4:
                        p0 = vertices.item(0).geometry.asVector()
                        p1 = vertices.item(1).geometry.asVector()
                        p2 = vertices.item(2).geometry.asVector()

                        if abs(d(p0, p1) * d(p1, p2) - face.area) < tolerance:
                            bad = False
                    if bad:
                        selections = [cmdInput.selection(j).entity
                                      for j in range(cmdInput.selectionCount)]
                        selections.remove(cmdInput.selection(i).entity)
                        cmdInput.clearSelection()

                        for c in selections:
                            cmdInput.addSelection(c)

                if cmdInput.selectionCount > 0:
                    edgeInput = args.inputs.itemById(dualEdgeSelectId)
                    if edgeInput:
                        edgeInput.hasFocus = True


        except:
            uimessage(self.ui, eventFailedMsg, traceback.format_exc())
