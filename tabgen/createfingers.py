import math

from collections import namedtuple

import adsk.core
import traceback

from adsk.core import Application
from adsk.core import ObjectCollection
from adsk.core import ValueInput
from adsk.fusion import Design
from adsk.fusion import FeatureOperations
from adsk.fusion import PatternDistanceType


from ..util import uimessage
from ..util import automaticWidthId, userDefinedWidthId

from .fingerface import FingerFace

# Constants

executionFailedMsg = 'TabGen execution failed: {}'
midplaneErrorMsg = 'Error finding two faces to create midplane: {} found.'

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

Point = namedtuple('Point', ['origin', 'xdir', 'ydir'])


def find_profile(sketch, distance, ui):
    """ Find profiles that have a side with the matching
        distance and return them in a list.
        """
    pList = [sketch.profiles.item(j)
             for j in range(sketch.profiles.count)]

    profiles = []

    for profile in pList:
        box = profile.boundingBox
        length = box.maxPoint.x - box.minPoint.x
        width = box.maxPoint.y - box.minPoint.y

        # round values to make sure that you can account for slight
        # deviation in F360 doubles, but leave acceptable accuracy
        if (round(length, 5) == round(distance, 5)
           or round(width, 5) == round(distance, 5)):
            profiles.append(profile)
        else:
            uimessage(ui, 'Profile not found for extrusion: l({}) w({}) d({})'.format(length, width, distance))
    return profiles


def extrude_profiles(sketch, mtlThick, face, extrude_count, xLen,
                     start_tab, ydir, xdir, tab_width, margin, finger_type=automaticWidthId, ui=None):
    # some function aliases
    CFO = FeatureOperations.CutFeatureOperation
    EDT = PatternDistanceType.ExtentPatternDistanceType
    createByReal = ValueInput.createByReal

    # Select the profile we want to use to make the nothces
    profs = adsk.core.ObjectCollection.create()

    profiles = find_profile(sketch, tab_width if start_tab else margin, ui)
    profs.add(profiles[1 if start_tab and len(profiles) > 1 else 0])

    # Define the extrusion extent to be -tabDepth.
    depth = createByReal(-mtlThick)
    xQuantity = createByReal(extrude_count)
    xDistance = createByReal(xLen)

    if start_tab is False and finger_type != automaticWidthId:
        connected = face.perpendicular_faces
        if len(connected) == 2:
            plane_count = face.planes.count
            planeInput = face.planes.createInput()
            planeInput.setByTwoPlanes(connected[0], connected[1])
            face.planes.add(planeInput)
            midplane = face.planes.item(plane_count)
        else:
            uimessage(ui, midplaneErrorMsg.format(len(connected)))

    # Cut the first notch.
    finger = face.extrudes.addSimple(profs, depth, CFO)

    inputEntities = ObjectCollection.create()
    inputEntities.add(finger)

    if start_tab is True or finger_type == automaticWidthId:
        patternInput = face.patterns.createInput(inputEntities,
                                                 face.parent.xConstructionAxis,
                                                 xQuantity,
                                                 xDistance,
                                                 EDT)
        patternInput.directionOneEntity = face.axis

        face.patterns.add(patternInput)

    else:
        if midplane.isValid:
            mirrorInput = face.mirrors.createInput(inputEntities,
                                                   midplane)
            face.mirrors.add(mirrorInput)


def get_faces(bfaces, ui=None):
    faces = []

    for face in bfaces:
        faces.append(FingerFace(face, ui))

    return faces


def first_point(sketch, vertical, margin, start_tab, ui):
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

    if start_tab:
        if vertical:
            o.y += (margin * ydir)
        else:
            o.x += (margin * xdir)

    return Point(o, xdir, ydir)


def second_point(point, vertical, thickness, width, margin=0, start_tab=True):
    awidth = width if start_tab else margin

    return adsk.core.Point3D.create(
                point.origin.x + (thickness if vertical else awidth)*point.xdir,
                point.origin.y + (awidth if vertical else thickness)*point.ydir,
                point.origin.z
            )


def create_fingers(finger_type, tab_width, mtlThick,
                   start_tab, selected_faces, app, ui=None):
    try:
        # For each selected face, determine face length, width, orientation,
        # origin, margin and number of tabs
        faces = get_faces(selected_faces, ui)

        for face in faces:
            if finger_type == userDefinedWidthId:
                default_tab_count = int(face.length // (2 * tab_width))
                tab_length = 2 * tab_width * default_tab_count
                margin = (face.length - tab_length + tab_width) / 2
                xLen = face.length - margin * 2 - tab_width
                extrude_count = default_tab_count

            elif finger_type == automaticWidthId:
                default_finger_count = max(3,
                                           math.floor(face.length / tab_width))
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
            sketch2 = face.parent.sketches.add(face.bface) if not start_tab else None

            fpoint = first_point(sketch, face.vertical, margin, start_tab, ui)
            spoint = second_point(fpoint,
                                  face.vertical,
                                  face.width,
                                  tab_width,
                                  margin,
                                  start_tab)

            # Get the collection of lines in the sketch
            lines = sketch.sketchCurves.sketchLines
            rectangle = lines.addTwoPointRectangle(fpoint.origin, spoint)
            sketch.sketchDimensions.addDistanceDimension(rectangle.item(0).startSketchPoint,
                                                         rectangle.item(0).endSketchPoint,
                                                         adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,
                                                         adsk.core.Point3D.create(5.5, -1, 0))

            extrude_profiles(sketch, mtlThick, face, extrude_count, xLen,
                             start_tab, fpoint.ydir, fpoint.xdir, tab_width, margin,
                             finger_type=finger_type, ui=ui)

            # Create the inner notches if the fingers are not starting at the end
            # of the face
            if not start_tab and finger_type != automaticWidthId:
                fpoint = first_point(sketch2, face.vertical, margin+tab_width, True, ui)
                spoint = second_point(fpoint,
                                      face.vertical,
                                      face.width,
                                      tab_width)

                lines = sketch2.sketchCurves.sketchLines
                lines.addTwoPointRectangle(fpoint.origin, spoint)
                extrude_profiles(sketch2, mtlThick, face, extrude_count, xLen,
                                 True, fpoint.ydir, fpoint.xdir, tab_width, margin, ui=ui)


        return True

    except:
        uimessage(ui, executionFailedMsg, traceback.format_exc())
