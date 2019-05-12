from adsk.core import Application

app = Application.get()
ui = app.userInterface


def uimessage(msg, value=None):
    if ui:
        if value is not None:
            ui.messageBox(msg.format(value))
        else:
            ui.messageBox(msg)
