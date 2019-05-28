import traceback

from adsk.core import Application
from adsk.core import SelectionCommandInput
from adsk.core import SelectionEventArgs
from adsk.core import SelectionEventHandler

from ..core import Face
from ..util import d
from ..util import distanceInputId
from ..util import dualEdgeSelectId
from ..util import fingerPlaceId
from ..util import lengthInputId
from ..util import parametricInputId
from ..util import selectedFaceInputId
from ..util import singleEdgeId
from ..util import automaticWidthId
from ..util import userDefinedWidthId

app = Application.get()
ui = app.userInterface


class SelectionEventHandler(SelectionEventHandler):

    def notify(self, args):
        eventArgs = SelectionEventArgs.cast(args)
        entity = eventArgs.selection.entity
        firingEvent = eventArgs.firingEvent
        activeSelectionInput = firingEvent.activeInput

        if activeSelectionInput.id == selectedFaceInputId or activeSelectionInput.id == dualEdgeSelectId:
            try:
                inputs = firingEvent.sender.commandInputs
                if inputs:
                    if activeSelectionInput.id == selectedFaceInputId:
                        face = Face(entity)

                        if face.is_edge and not face.is_completed:
                            edgeSelect = SelectionCommandInput.cast(inputs.itemById(dualEdgeSelectId))
                            if edgeSelect.selectionCount == 1:
                                eventArgs.isSelectable = face.isParallelToLine(edgeSelect.selection(0).entity)
                            else:
                                eventArgs.isSelectable = True
                        else:
                            eventArgs.isSelectable = False

                    elif activeSelectionInput.id == dualEdgeSelectId:
                        if activeSelectionInput.selectionCount == 0:
                            faceSelect = SelectionCommandInput.cast(inputs.itemById(selectedFaceInputId))
                            if faceSelect.selectionCount == 1:
                                face = Face(faceSelect.selection(0).entity)
                                eventArgs.isSelectable = face.isParallelToLine(entity)
                        else:
                            eventArgs.isSelectable = False
            except:
                ui.messageBox(traceback.format_exc())
        else:
            eventArgs.isSelectable = True
