import traceback

from adsk.core import Application
from adsk.core import InputChangedEventHandler

from ..util import d
from ..util import distanceInputId
from ..util import dualEdgeSelectId
from ..util import fingerPlaceId
from ..util import lengthInputId
from ..util import parametricInputId
from ..util import selectedFaceInputId
from ..util import singleEdgeId

from ..util import automaticWidthId
from ..core import Face

app = Application.get()
ui = app.userInterface
# Constants

eventFailedMsg = 'TabGen input changed event failed: {}'

tolerance = 0.001


class InputChangedHandler(InputChangedEventHandler):

    def notify(self, args):
        try:
            cmdInput = args.input
            # If it is the selection input that got changed, check
            # that the selections are all a rectangles; deslelect
            # those that are not.
            faceInput = args.inputs.itemById(selectedFaceInputId)
            edgeInput = args.inputs.itemById(dualEdgeSelectId)
            parametricInput = args.inputs.itemById(parametricInputId)
            lengthInput = args.inputs.itemById(lengthInputId)
            distanceInput = args.inputs.itemById(distanceInputId)
            dualInput = args.inputs.itemById(dualEdgeSelectId)
            placeInput = args.inputs.itemById(fingerPlaceId)

            if cmdInput.id == fingerPlaceId and placeInput:
                if placeInput.selectedItem.name == singleEdgeId:
                    distanceInput.isVisible = False
                    dualInput.isVisible = False
                    edgeInput.clearSelection()
                    if edgeInput.hasFocus is True:
                        faceInput.hasFocus = True

                    edgeInput.isEnabled = False
                else:
                    distanceInput.isVisible = True
                    dualInput.isVisible = True
                    edgeInput.isEnabled = True

            if (cmdInput.id in [selectedFaceInputId,
                                dualEdgeSelectId,
                                fingerPlaceId]):
                if faceInput.selectionCount > 0:
                    if edgeInput and edgeInput.selectionCount == 0:
                        edgeInput.hasFocus = True

                    face = Face(faceInput.selection(0).entity)
                    lengthInput.value = face.length

                    if edgeInput.selectionCount > 0:
                        distanceInput.value = Face.distance_between(face, edgeInput.selection(0).entity)
                    else:
                        distanceInput.value = 0

        except:
            ui.messageBox(eventFailedMsg.format(traceback.format_exc()))
