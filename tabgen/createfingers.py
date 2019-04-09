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


Face = namedtuple('Face', ['length', 'width', 'vertical', 'bface'])


def get_faces(bfaces):
    faces = []

    for face in bfaces:
        pRange = face.evaluator.parametricRange()
        length = pRange.maxPoint.x - pRange.minPoint.x
        width = pRange.maxPoint.y - pRange.minPoint.x

        if (pRange.maxPoint.y > pRange.maxPoint.x):
            faces.append(Face(width, length, True, face))
        else:
            faces.append(Face(length, width, False, face))

    return faces


def first_point(face):
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


def create_fingers(finger_type, tab_width, mtlThick, start_tab, bfaces, app, ui=None):
    try:
        # For each selected face, determine face length, width, orientation,
        # origin, margin and number of tabs
        faces = get_faces(bfaces)

        for face in faces:
            sketch = face.bface.body.parentComponent.sketches.add(face.bface)

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

            xLen = 0
            if finger_type == 'User-Defined Width':
                default_tab_count = int(face.length // (2 * tab_width))
                margin = (face.length - 2 * tab_width * default_tab_count + tab_width) / 2
                xLen = face.length - margin*2 - tab_width
                extrude_count = default_tab_count
            elif finger_type == 'Automatic Width':
                default_finger_count = max(3, math.floor(face.length / tab_width))
                default_tab_width = face.length / default_finger_count
                default_notch_count = math.floor(default_finger_count/2)

                if start_tab:
                    extrude_count = default_notch_count
                    xLen = (default_finger_count - 3)*default_tab_width
                else:
                    extrude_count = default_finger_count - default_notch_count
                    xLen = (default_finger_count - 1)*default_tab_width

                tab_width = default_tab_width
                margin = tab_width

            if face.vertical:
                o.y += (margin * ydir)
            else:
                o.x += (margin * xdir)

            # Get the collection of lines in the sketch
            lines = sketch.sketchCurves.sketchLines

            # Define the extrusion extent to be -tabDepth.
            distance = adsk.core.ValueInput.createByReal(-mtlThick)

            lines.addTwoPointRectangle(o, adsk.core.Point3D.create(
                o.x + (mtlThick if face.vertical else tab_width)*xdir,
                o.y + (tab_width if face.vertical else mtlThick)*ydir,
                o.z
                )
            )

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

            parent = face.bface.body.parentComponent
            # Cut the notches. Do it in one operation to keep the timeline neat
            extrudes = face.bface.body.parentComponent.features.extrudeFeatures
            finger = extrudes.addSimple(
                profs,
                distance,
                adsk.fusion.FeatureOperations.CutFeatureOperation)

            inputEntities = adsk.core.ObjectCollection.create()
            inputEntities.add(finger)

            xQuantity = adsk.core.ValueInput.createByReal(extrude_count)
            xDistance = adsk.core.ValueInput.createByReal(xLen)

            rectangularPatterns = face.bface.body.parentComponent.features.rectangularPatternFeatures
            if xDistance:
                rectangularPatternInput = rectangularPatterns.createInput(inputEntities,
                                                                          parent.xConstructionAxis,
                                                                          xQuantity,
                                                                          xDistance,
                                                                          adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)

            pattern = rectangularPatterns.add(rectangularPatternInput)

        return True

    except:
        uimessage(ui, executionFailedMsg, traceback.format_exc())
