from .axisdir import axis_dir
from .distance import d
from .uimessage import uimessage
from .vertical import vertical

errorMsgInputId = 'errorMsgCommandInput'
mtlThickInputId = 'mtlThickValueCommandInput'
selectedFaceInputId = 'selectedFaceCommandInput'
startWithTabInputId = 'startWithTabCommandInput'
tabGenCommandId = 'tabGenCommandButton'
tabWidthInputId = 'tabWidthValueCommandInput'
fingerTypeId = 'fingerTypeInput'
fingerPlaceId = 'fingerPlaceInput'
dualSidesInputId = 'dualSidesCommandInput'
dualEdgeSelectId = 'dualEdgeSelectInput'
parametricInputId = 'parametricInput'
lengthInputId = 'lengthCommandInput'
distanceInputId = 'distanceCommandInput'

userDefinedWidthId = 'User-Defined Width'
automaticWidthId = 'Automatic Width'

singleEdgeId = 'Single Edge'
dualEdgeId = 'Dual Edge'


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
