import traceback

from collections import namedtuple

from adsk.core import CommandCreatedEventHandler
from adsk.core import DropDownStyles as dds
from adsk.core import CommandEventHandler

from .. import definitions as defs
from .. import fusion

Item = namedtuple('Item', ['id_', 'enabled'])

initializedFailedMsg = 'TabGen initialization failed: {}'


class ExecuteHandler(CommandEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui

    def notify(self, args):
        command = args.firingEvent.sender

        try:
            first_inputs = command.commandInputs
            parent_inputs = first_inputs.command.commandInputs if first_inputs.command else first_inputs

            face = parent_inputs.itemById(defs.selectedFaceInputId).selection(0).entity
            if not face:
                self.ui.messageBox('No face found.')

            sketch = face.body.parentComponent.sketches.add(face)
            # Let's project the face outside edges into the sketch.
            # This makes it easier to find the axes for duplicating
            # fingers across opposing sides of the body

            # coordinates = []
            # for edge in face.edges:
            #     # line = sketch.project(edge)
            #     line.isConstruction = True
                # start = edge.startVertex.geometry
                # end = edge.endVertex.geometry
                # coordinates.append('Start: {}. {}. {}\nEnd: {}, {}, {}'.format(round(start.x, 2), round(start.y, 2), round(start.z, 2),
                #                                                                round(end.x, 2), round(end.y, 2), round(end.z, 2)))


            # self.ui.messageBox('\n'.join(coordinates))
            self.ui.messageBox('Testing')
            lines = sketch.sketchCurves.sketchLines
            border = fusion.Rectangle(lines[0:4])
            # for line in lines:
            #     start = line.startSketchPoint.geometry
            #     end = line.endSketchPoint.geometry
            #     startw = line.startSketchPoint.worldGeometry
            #     endw = line.endSketchPoint.worldGeometry
            #
                # coordinates.append('S: {}, {}, {} -- E: {}, {}, {} -- SW: {}, {}, {} -- EW: {}, {}, {}'.format(
                #     round(start.x, 2), round(start.y, 2), round(start.z, 2),
                #     round(end.x, 2), round(end.y, 2), round(end.z, 2),
                #     round(startw.x, 2), round(startw.y, 2), round(startw.z, 2),
                #     round(endw.x, 2), round(endw.y, 2), round(endw.z, 2)
                # ))

            start = fusion.next_point(start=border.bottom.left.geometry,
                                      length=1,
                                      width=0,
                                      vertical=border.is_vertical,
                                      ui=self.ui)
            end = fusion.next_point(start=start,
                                    length=.8,
                                    width=.2,
                                    vertical=border.is_vertical,
                                    ui=self.ui)
            finger = lines.addTwoPointRectangle(start, end)
            # line.isConstruction = False
            self.ui.messageBox('Border Vertical: {}'.format(str(border.is_vertical)))
            self.ui.messageBox('Bottom Vertical: {}'.format(str(border.bottom.is_vertical)))
            self.ui.messageBox('Bottom Reversed: {}'.format(str(border.bottom.reversed)))
            be = border.bottom.line.endSketchPoint.geometry
            bs = border.bottom.line.startSketchPoint.geometry
            self.ui.messageBox('Bottom: {}, {}, {} -- {}, {}, {}'.format(bs.x, bs.y, bs.z,
                                                                         be.x, be.y, be.z))

            # self.ui.messageBox('\n'.join(coordinates))

        except:

            self.ui.messageBox(initializedFailedMsg.format(traceback.format_exc()))


class SketchPanel(CommandCreatedEventHandler):

    def __init__(self, app, ui):
        super().__init__()
        self.app = app
        self.ui = ui
        self.handlers = []

    def add_dropdown(self, inputs, id_, name, items):
        input_ = inputs.addDropDownCommandInput(id_,
                                                name,
                                                dds.TextListDropDownStyle)
        listItems = input_.listItems
        for item in items:
            listItems.add(item.id_,
                          item.enabled)

    def add_selection(self, inputs, id_, name, help_, filter_, min_, max_):
        input_ = inputs.addSelectionInput(
            id_,
            name,
            help_
            )
        input_.addSelectionFilter(filter_)
        input_.setSelectionLimits(min_, max_)

    def notify(self, args):
        try:
            document = self.app.activeDocument
            design = self.app.activeProduct

            if document.isSaved is not True:
                self.ui.messageBox('Please save your document before continuing.')

            else:
                cmd = args.command

                # Set up the inputs
                cmd_inputs = cmd.commandInputs

                # Add onExecute event handler
                execute = ExecuteHandler(self.app, self.ui)
                cmd.execute.add(execute)
                self.handlers.append(execute)

                main_input = cmd_inputs.addTabCommandInput('mainTabInput', 'Main')
                inputs = main_input.children

                self.add_selection(inputs, defs.selectedFaceInputId, 'Face', 'Faces where tabs will be cut.',
                                   'PlanarFaces', 1, 1)

        except:
            self.ui.messageBox('{}:\n{}'.format(initializedFailedMsg,
                                                traceback.format_exc(3)))
