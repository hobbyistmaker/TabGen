import adsk.core
import traceback

from ..util import d
from ..util import distanceInputId
from ..util import dualEdgeSelectId
from ..util import fingerPlaceId
from ..util import lengthInputId
from ..util import parametricInputId
from ..util import selectedFaceInputId
from ..util import singleEdgeId
from ..util import uimessage
from ..util import automaticWidthId
from ..util import userDefinedWidthId

from ..tabgen import FingerFace


class SelectionEventHandler(adsk.core.SelectionEventHandler):

    def notify(self, args):
        eventArgs = adsk.core.SelectionEventArgs.cast(args)
        activeSelectionInput = eventArgs.firingEvent.activeInput

        if activeSelectionInput.id == selectedFaceInputId or activeSelectionInput.id == dualEdgeSelectId:
            inputs = eventArgs.firingEvent.sender.commandInputs

            if activeSelectionInput.id == selectedFaceInputId:
                face = eventArgs.selection.entity
                if FingerFace.create(automaticWidthId, face).is_edge:
                    eventArgs.isSelectable = True
                else:
                    eventArgs.isSelectable = False

        else:
            eventArgs.isSelectable = True
