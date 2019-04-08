import math

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
# tabWidth:     The width each tab and gap should be (mm).
# mtlThick:     The thickness of the material being cut (mm).
# startWithTab: True if the margins (the areas at ends of the face) are to be
#               tabs; False if they are to be cut away.
# faces:        A list of BRepFace objects representing the selected faces.

app = Application.get()
product = app.activeProduct
design = Design.cast(product)
root = design.rootComponent


def create_fingers(fingerType, tabWidth, mtlThick, startWithTab, faces, app, ui=None):
    try:
        faceLen = []
        faceWid = []
        vert = []
        sketch = []
        nFaces = len(faces)

        # For each selected face, determine face length, width, orientation,
        # origin, margin and number of tabs
        for i in range(nFaces):
            pRange = faces[i].evaluator.parametricRange()

            vert.append(False)
            faceLen.append(pRange.maxPoint.x - pRange.minPoint.x)
            faceWid.append(pRange.maxPoint.y - pRange.minPoint.y)
            if (pRange.maxPoint.y > pRange.maxPoint.x):
                vert[i] = True
                t = faceLen[i]
                faceLen[i] = faceWid[i]
                faceWid[i] = t

        # Create a sketch on each selected face that creates the profiles we
        # need to cut the gaps between the tabs
        for i in range(nFaces):
            # Create a new sketch on face[i].
            sketch.append(faces[i].body.parentComponent.sketches.add(faces[i]))

            # Hard-won knowledge: When a sketch is made on a rectangular face,
            # (0,0) and the endpoints of the edges of the face are projected
            # into the sketchPoints. This is not documented that I can find,
            # but it's true.
            o = sketch[i].sketchPoints.item(1).geometry
            xdir = 1
            ydir = 1

            for j in range(1, sketch[i].sketchPoints.count):
                item = sketch[i].sketchPoints.item(j)
                ix = item.geometry.x
                iy = item.geometry.y
                # tox = o.x
                # toy = o.y

                if ((ix < o.x and ix >= 0)
                   or (ix > o.x and ix <= 0)):
                    xdir = -1 if (ix > o.x and ix <= 0) else 1
                    o.x = ix

                if ((iy < o.y and iy >= 0)
                   or (iy > o.y and iy <= 0)):
                    ydir = -1 if (iy > o.y and iy <= 0) else 1
                    o.y = iy

                # uimessage(ui, '{}, {}, {}, {}, {}, {}'.format(tox, toy, ix, iy, xdir, ydir))

            # uimessage(ui, '{}, {}, {}, {}, {}, {}'.format(o.x, o.y, mtlThick, tabWidth, xdir, ydir))

            xLen = 0
            if fingerType == 'User-Defined Width':
                nTabs = int(faceLen[i] // (2 * tabWidth))
                margin = (faceLen[i] - 2 * tabWidth * nTabs + tabWidth) / 2
                xLen = faceLen[i] - margin*2 - tabWidth
            elif fingerType == 'Automatic Width':
                default_finger_count = max(3, math.floor(faceLen[i] / tabWidth))
                default_tab_width = faceLen[i] / default_finger_count
                default_notch_count = math.floor(default_finger_count/2)
                xLen = (default_finger_count - 3)*default_tab_width

                tabWidth = default_tab_width
                margin = tabWidth
                nTabs = default_notch_count


            if vert[i]:
                o.y += (margin * ydir)
            else:
                o.x += (margin * xdir)

            # Get the collection of lines in the sketch
            lines = sketch[i].sketchCurves.sketchLines

            # Define the extrusion extent to be -tabDepth.
            distance = adsk.core.ValueInput.createByReal(-mtlThick)

            lines.addTwoPointRectangle(o, adsk.core.Point3D.create(
                o.x + (mtlThick if vert[i] else tabWidth)*xdir,
                o.y + (tabWidth if vert[i] else mtlThick)*ydir,
                o.z
                )
            )

            # # Create the profiles we need for the tabs and gaps
            # for j in range(nTabs):
            #     lines.addTwoPointRectangle(o, adsk.core.Point3D.create(
            #         o.x + (mtlThick if vert[i] else tabWidth),
            #         o.y + (tabWidth if vert[i] else mtlThick),
            #         o.z))
            #     # update origin for next tab
            #     if vert[i]:
            #         o.y += 2 * tabWidth
            #     else:
            #         o.x += 2 * tabWidth

        # Cut the gaps between tabs on each selected face
        for i in range(nFaces):
            # Collect and then sort all the profiles we created
            pList = [sketch[i].profiles.item(j)
                     for j in range(sketch[i].profiles.count)]
            if vert[i]:
                pList.sort(key=lambda profile: profile.boundingBox.minPoint.y,
                           reverse=True)
            else:
                pList.sort(key=lambda profile: profile.boundingBox.minPoint.x,
                           reverse=True)

            # Select the ones we want to use to make the gaps
            profs = adsk.core.ObjectCollection.create()
            for j in range(1 if startWithTab else 0, len(pList), 2):
                profs.add(pList[j])

            parent = faces[i].body.parentComponent
            # Cut the gaps. Do it in one operation to keep the timeline neat
            extrudes = faces[i].body.parentComponent.features.extrudeFeatures
            finger = extrudes.addSimple(
                profs,
                distance,
                adsk.fusion.FeatureOperations.CutFeatureOperation)

            inputEntities = adsk.core.ObjectCollection.create()
            inputEntities.add(finger)

            xQuantity = adsk.core.ValueInput.createByReal(nTabs)
            xDistance = adsk.core.ValueInput.createByReal(xLen)

            rectangularPatterns = faces[i].body.parentComponent.features.rectangularPatternFeatures
            if xDistance:
                rectangularPatternInput = rectangularPatterns.createInput(inputEntities,
                                                                          parent.xConstructionAxis,
                                                                          xQuantity,
                                                                          xDistance,
                                                                          adsk.fusion.PatternDistanceType.ExtentPatternDistanceType)

            pattern = rectangularPatterns.add(rectangularPatternInput)
            # pattern.quantityOne.expression = 'floor(max(3; ( floor(ceil(length / fingerw) / 2) * 2 ) - 1))/2'
            # pattern.distanceOne.expression = 'length - fingerw*3'

        return True

    except:
        uimessage(ui, executionFailedMsg, traceback.format_exc())
