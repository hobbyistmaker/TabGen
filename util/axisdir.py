from adsk.core import Application
app = Application.get()
ui = app.userInterface


def axis_dir(vector):
    # ui.messageBox('Axis Vector: {} {} {}'.format(vector.x, vector.y, vector.z))
    if vector.z:
        return 'z'
    if vector.y:
        return 'y'
    return 'x'
