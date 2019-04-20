import math

errorMsgInputId = 'errorMsgCommandInput'
mtlThickInputId = 'mtlThickValueCommandInput'
selectedFaceInputId = 'selectedFaceCommandInput'
startWithTabInputId = 'startWithTabCommandInput'
tabGenCommandId = 'tabGenCommandButton'
tabWidthInputId = 'tabWidthValueCommandInput'
fingerTypeId = 'fingerTypeInput'
dualSidesInputId = 'dualSidesCommandInput'
dualEdgeSelectId = 'dualEdgeSelectInput'

userDefinedWidthId = 'User-Defined Width'
automaticWidthId = 'Automatic Width'


def d(a, b):
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)


def uimessage(ui, msg, value=None):
    if ui:
        if value is not None:
            ui.messageBox(msg.format(value))
        else:
            ui.messageBox(msg)


__all__ = [d,
           automaticWidthId,
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
           userDefinedWidthId
           ]
