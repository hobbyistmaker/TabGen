from collections import namedtuple

from .. import definitions as defs
from .. import fusion

from .fingermanager import FingerManager

class InvalidFaceSelected(Exception): pass

class FaceNotExists(Exception): pass


def create(app, ui, inputs):
    face = inputs.selected_face

    if face is None or face.isValid is False:
        raise InvalidFaceSelected

    sketch = face.body.parentComponent.sketches.add(face)

    lines = sketch.sketchCurves.sketchLines

    # Let's project the face outside edges into the sketch.
    # This makes it easier to find the axes for duplicating
    # fingers across opposing sides of the body
    for edge in face.edges[0:4]:
        ref = sketch.project(edge)

    # Change the default edges into construction lines so that
    # we don't have unneeded profiles in the sketch
    for line in lines[0:4]:
        line.isConstruction = True

    # Create a border object from the projected edges
    # and make them construction lines to prevent unneeded
    # profiles in the sketch
    border = fusion.Rectangle(lines[4:8])
    border.make_construction()

    name = inputs.selected_body.name
    orientation = fusion.face_orientation(face)
    face_id = fusion.add_face(face)
    name = '{name} {orientation}{face_num}'.format(name=name,
                                                   orientation=orientation,
                                                   face_num=face_id)
    alias = fusion.clean_string(name)

    sketch.name = '{} Finger Sketch'.format(name)

    manager = FingerManager(app, ui, inputs, name, alias, border)
    manager.draw(sketch)
