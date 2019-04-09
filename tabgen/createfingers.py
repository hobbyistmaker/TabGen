import math

from collections import namedtuple

import adsk.core
import traceback

from adsk.core import Application
from adsk.fusion import Design


from ..util import uimessage

# Constants

executionFailedMsg = 'TabGen execution failed: {}'

# Actually lay out and cut the slots to make the tabs on the selected faces.
# It is assumed that the inputs have all been validated.
#
# tab_width:    The width each tab and gap should be (mm).
# mtlThick:     The thickness of the material being cut (mm).
# start_tab:    True if the margins (the areas at ends of the face) are to be
#               tabs; False if they are to be cut away.
# faces:        A list of BRepFace objects representing the selected faces.

app = Application.get()
product = app.activeProduct
design = Design.cast(product)
root = design.rootComponent


Face = namedtuple('Face', ['length',
                           'width',
                           'vertical',
                           'bface',
                           'parent',
                           'extrudes',
                           'patterns'])

Point = namedtuple('Point', ['origin', 'xdir', 'ydir'])


def get_faces(bfaces):
    faces = []

    for face in bfaces:
        pRange = face.evaluator.parametricRange()
        length = pRange.maxPoint.x - pRange.minPoint.x
        width = pRange.maxPoint.y - pRange.minPoint.x
        parent = face.body.parentComponent
        extrudes = parent.features.extrudeFeatures
        patterns = parent.features.rectangularPatternFeatures

        if (pRange.maxPoint.y > pRange.maxPoint.x):
            faces.append(Face(width,
                              length,
                              True,
                              face,
                              parent,
                              extrudes,
                              patterns
                              ))
        else:
            faces.append(Face(length,
                              width,
                              False,
                              face,
                              parent,
                              extrudes,
                              patterns))

    return faces


def first_point(sketch, vertical, margin):
    # Hard-won knowledge: When a sketch is made on a rectangular face,
    # (0,0) and the endpoints of the edges of the face are projected
    # into the sketchPoints. This is not documented that I can find,
    # but it's true.
    o = sketch.sketchPoints.item(1).geometry
    xdir = 1
    ydir = 1

    for j in range(1, sketch.sketchPoints.count):
        item = sketch.sketchPoints.item(j)
        ix = item.geometry.x
        iy = item.geometry.y

        if ((ix < o.x and ix >= 0)
           or (ix > o.x and ix <= 0)):
            xdir = -1 if (ix > o.x and ix <= 0) else 1
            o.x = ix

        if ((iy < o.y and iy >= 0)
           or (iy > o.y and iy <= 0)):
            ydir = -1 if (iy > o.y and iy <= 0) else 1
            o.y = iy

    if vertical:
        o.y += (margin * ydir)
    else:
        o.x += (margin * xdir)

    return Point(o, xdir, ydir)


def second_point(point, vertical, thickness, width):
    return adsk.core.Point3D.create(
                point.origin.x + (thickness if vertical else width)*point.xdir,
                point.origin.y + (width if vertical else thickness)*point.ydir,
                point.origin.z
            )


def create_fingers(finger_type, tab_width, mtlThick, start_tab, bfaces, app, ui=None):
    try:
        # For each selected face, determine face length, width, orientation,
        # origin, margin and number of tabs
        faces = get_faces(bfaces)

        for face in faces:
            if finger_type == 'User-Defined Width':
                default_tab_count = int(face.length // (2 * tab_width))
                tab_length = 2 * tab_width * default_tab_count
                margin = (face.length - tab_length + tab_width) / 2
                xLen = face.length - margin * 2 - tab_width
                extrude_count = default_tab_count

            elif finger_type == 'Automatic Width':
                default_finger_count = max(3, math.floor(face.length / tab_width))
                default_tab_width = face.length / default_finger_count
                default_notch_count = math.floor(default_finger_count/2)

                if start_tab:
                    extrude_count = default_notch_count
                    xLen = (default_finger_count - 3) * default_tab_width
                else:
                    extrude_count = default_finger_count - default_notch_count
                    xLen = (default_finger_count - 1) * default_tab_width

                tab_width = default_tab_width
                margin = tab_width

            sketch = face.parent.sketches.add(face.bface)
            fpoint = first_point(sketch, face.vertical, margin)

            # Get the collection of lines in the sketch
            lines = sketch.sketchCurves.sketchLines
            lines.addTwoPointRectangle(fpoint.origin,
                                       second_point(fpoint,
                                                    face.vertical,
                                                    mtlThick,
                                                    tab_width))

            # Collect and then sort all the profiles we created
            pList = [sketch.profiles.item(j)
                     for j in range(sketch.profiles.count)]
            if face.vertical:
                pList.sort(key=lambda profile: profile.boundingBox.minPoint.y,
                           reverse=True)
            else:
                pList.sort(key=lambda profile: profile.boundingBox.minPoint.x,
                           reverse=True)

            # Select the profile we want to use to make the nothces
            profs = adsk.core.ObjectCollection.create()
            profs.add(pList[1 if start_tab else 0])

            # Define the extrusion extent to be -tabDepth.
            distance = adsk.core.ValueInput.createByReal(-mtlThick)

            # Cut the notches. Do it in one operation to keep the timeline neat
            finger = face.extrudes.addSimple(
                profs,
                distance,
                adsk.fusion.FeatureOperations.CutFeatureOperation)

            inputEntities = adsk.core.ObjectCollection.create()
            inputEntities.add(finger)

            xQuantity = adsk.core.ValueInput.createByReal(extrude_count)
            xDistance = adsk.core.ValueInput.createByReal(xLen)
            patterns = face.patterns

            if not face.vertical:
                if xDistance:
                    patternInput = patterns.createInput(inputEntities,
                                                        face.parent.xConstructionAxis,
                                                        xQuantity,
                                                        xDistance,
                                                        adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)
            else:
                ### BREAKS FOR VERTICAL
                if xDistance:
                    patternInput = patterns.createInput(inputEntities,
                                                        face.parent.yConstructionAxis,
                                                        xQuantity,
                                                        xDistance,
                                                        adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)


            pattern = patterns.add(patternInput)

        return True

    except:
        uimessage(ui, executionFailedMsg, traceback.format_exc())
