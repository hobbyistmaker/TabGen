<<<<<<< HEAD
import math

from .axisdir import axis_dir
=======
from .axisdir import axis_dir
from .distance import d
from .uimessage import uimessage
from .vertical import vertical
>>>>>>> e2f26244acac2be259deff5f18dcc50d954f34a2

errorMsgInputId = 'errorMsgCommandInput'
mtlThickInputId = 'mtlThickValueCommandInput'
selectedFaceInputId = 'selectedFaceCommandInput'
startWithTabInputId = 'startWithTabCommandInput'
tabGenCommandId = 'tabGenCommandButton'
tabWidthInputId = 'tabWidthValueCommandInput'
fingerTypeId = 'fingerTypeInput'
<<<<<<< HEAD
dualSidesInputId = 'dualSidesCommandInput'
dualEdgeSelectId = 'dualEdgeSelectInput'
parametricInputId = 'parametricInput'
=======
fingerPlaceId = 'fingerPlaceInput'
dualSidesInputId = 'dualSidesCommandInput'
dualEdgeSelectId = 'dualEdgeSelectInput'
parametricInputId = 'parametricInput'
lengthInputId = 'lengthCommandInput'
distanceInputId = 'distanceCommandInput'
>>>>>>> e2f26244acac2be259deff5f18dcc50d954f34a2

userDefinedWidthId = 'User-Defined Width'
automaticWidthId = 'Automatic Width'

<<<<<<< HEAD

def d(a, b):
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)


def uimessage(ui, msg, value=None):
    if ui:
        if value is not None:
            ui.messageBox(msg.format(value))
        else:
            ui.messageBox(msg)
=======
singleEdgeId = 'Single Edge'
dualEdgeId = 'Dual Edge'
>>>>>>> e2f26244acac2be259deff5f18dcc50d954f34a2


__all__ = [d,
           automaticWidthId,
           axis_dir,
           dualSidesInputId,
           dualEdgeSelectId,
           errorMsgInputId,
           fingerTypeId,
           mtlThickInputId,
           selectedFaceInputId,
           startWithTabInputId,
           tabGenCommandId,
           tabWidthInputId,
           uimessage,
           userDefinedWidthId,
           vertical
           ]
