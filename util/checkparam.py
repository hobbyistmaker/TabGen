import traceback

from adsk.core import Application
from adsk.fusion import Design
from adsk.core import ValueInput

app = Application.get()
ui = app.userInterface
des = Design.cast(app.activeProduct)

all_params = des.allParameters
user_params = des.userParameters

createByReal = ValueInput.createByReal


def set_value(itemParam, name, value, units='cm'):
    inputValue = str(value)
    itemParam = user_params.add(name, createByReal(0), units, 'Auto-generated Parameter')
    itemParam.expression = inputValue
    return itemParam


def check_param(name, value, units='cm'):
    try:
        itemParam = user_params.itemByName(name)
        if not itemParam:
            set_value(itemParam, name, value, units)
    except:
        ui.messageBox(traceback.format_exc(1))
