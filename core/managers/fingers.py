from collections import namedtuple

from .. import definitions as defs
from .. import fusion

from .fingermanager import FingerManager

def create(app, ui, inputs):
    orientation = fusion.face_orientation(inputs.selected_face)
    face_id = fusion.add_face(inputs.selected_face)
    name = '{name} {orientation}{face_num}'.format(name=inputs.selected_body.name,
                                                   orientation=orientation,
                                                   face_num=face_id)
    alias = fusion.clean_string(name)

    sketch = inputs.selected_body.parentComponent.sketches.add(inputs.selected_face)
    sketch.name = '{} Finger Sketch'.format(name)

    lines = sketch.sketchCurves.sketchLines

    # Let's project the face outside edges into the sketch.
    # This makes it easier to find the axes for duplicating
    # fingers across opposing sides of the body
    for line in inputs.selected_face.edges[0:4]:
        ref = sketch.project(line)

    # Change the default edges into construction lines so that
    # we don't have unneeded profiles in the sketch
    for line in lines[0:4]:
        line.isConstruction = True

    # Create a border object from the projected edges
    # and make them construction lines to prevent unneeded
    # profiles in the sketch
    border = fusion.Rectangle(sketch.sketchCurves.sketchLines[4:8])
    border.make_construction()

    manager = FingerManager(app, ui, inputs, name, alias, border)
    manager.draw(sketch)
