import re
import copy
from typing import List
from pivy import coin
from enum import Enum
from math import pi
from random import randrange
from pivy import coin

import rdwr.threedvector as vector
import util

from rdwr.threedvector import (Point, Direction)
from rdwr.viewpoint import (OrthogonalCamera, PerspectiveCamera, Component,
        ComponentColour, Line, ClippingPlane)

# it is assumed that this file is only imported iff the plugin is running inside
# FreeCAD in Gui mode.
import FreeCADGui
import FreeCAD
draftAvailable = True
try:
    import Draft
except:
    util.printInfo("Cannot import Draft workbench. No elements can be drawn")
    draftAvailable = False


pCamClassTypeId = coin.SoPerspectiveCamera_getClassTypeId
oCamClassTypeId = coin.SoOrthographicCamera_getClassTypeId

doc = FreeCAD.ActiveDocument
""" Reference to the document the model to the BCF file is open in """

bcfGroupName = "BCF-{}".format(randrange(5000))
bcfGroup = None
""" Reference to the document object group all elements will be assigned to,
that get created by functions inside this file """

clipPlanes = list()
""" List of all currently active clipping planes """


class CamType(Enum):
    ORTHOGONAL = 1
    PERSPECTIVE = 2

class Unit(Enum):
    METER = 1
    MMETER = 2
    INCH = 3
    CMETER = 4
    FOOT = 5


def getConversionFactor(srcUnit: Unit, dstUnit: Unit = Unit.MMETER):

    """ Returns the conversion factor to get a value from the `srcUnit` into
    `dstUnit`.

    Currently only conversion factors for the destination unit METER are
    returned
    """

    conversionFactor = None
    if srcUnit == Unit.METER:
        conversionFactor = 1000
    elif srcUnit == Unit.MMETER:
        conversionFactor = 1
    elif srcUnit == Unit.INCH:
        conversionFactor = 25.4
    elif srcUnit == Unit.CMETER:
        conversionFactor = 10
    elif srcUnit == Unit.FOOT:
        conversionFactor = 304.8

    return conversionFactor


def degreeToRadians(degrees):

    """ Convert a value in degrees into radians """

    return degrees * pi / 180


def convertToFreeCADUnits(vector: FreeCAD.Vector = None,
        distance: float = None, srcUnit: Unit = Unit.METER):

    """ Convert a FreeCAD.Vector or a simple distance to millimeters as used by
    FreeCAD.

    It can convert all values from the units specified in the `Unit` Enum to
    millimeters.
    """

    conversionFactor = getConversionFactor(srcUnit, Unit.MMETER) # meter to millimeter

    newVal = None
    if vector is not None:
        newVal = FreeCAD.Vector(vector.x * conversionFactor,
                vector.y * conversionFactor,
                vector.z * conversionFactor)
    elif distance is not None:
        newVal = distance * conversionFactor

    return newVal


def getRotation(normal: FreeCAD.Vector, up: FreeCAD.Vector):

    """ Converts vectors normal and up into an affine rotation matrix """

    # setting up axis vectors as normal vectors with cross product
    # X = Y x Z
    # Y = Z x X -- to guarantee that Y is equal in length to x and z
    z = normal
    y = up
    x = y.cross(z)
    y = z.cross(x)

    rot = FreeCAD.Matrix()
    rot.A11 = x.x
    rot.A21 = x.y
    rot.A31 = x.z

    rot.A12 = y.x
    rot.A22 = y.y
    rot.A32 = y.z

    rot.A13 = z.x
    rot.A23 = z.y
    rot.A33 = z.z

    return FreeCAD.Placement(rot).Rotation


def setCamera(camViewpoint: vector.Point,
        camDirection: vector.Direction,
        camUpVector: vector.Direction):

    """ Sets the position and rotation of the camera.

    Position is given by camViewpoint and the rotation is given by camUpVector
    and camDirection.
    This function assumes that it is running inside FreeCAD in Gui mode and thus
    does not make any checks in that direction.
    """

    cam = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()

    fPosition = FreeCAD.Vector(camViewpoint.x, camViewpoint.y, camViewpoint.z)
    fUpVector = FreeCAD.Vector(camUpVector.x, camUpVector.y, camUpVector.z)
    fDirVector = FreeCAD.Vector(camDirection.x, camDirection.y, camDirection.z)

    # convert the vectors units to the unit FreeCAD uses
    fPosition = convertToFreeCADUnits(vector = fPosition, srcUnit = Unit.METER)
    fUpVector = convertToFreeCADUnits(vector = fUpVector, srcUnit = Unit.METER)
    fDirVector = convertToFreeCADUnits(vector = fDirVector, srcUnit = Unit.METER)

    rotation = getRotation(fDirVector, fUpVector)

    cam.orientation.setValue(rotation.Q)
    cam.position.setValue(fPosition)

    return cam


def setPCamera(camSettings: PerspectiveCamera):

    """ Sets the camera's position, orientation and fieldOfView to `camSettings`.

    If the camera in the current view is not a Perspective camera, it is changed
    by calling View3DInventorPy.setCameraType("Perspective").
    The field of view is set by setting the value `heightAngle` in
    SoPerspectiveCamera.
    """

    view = FreeCADGui.ActiveDocument.ActiveView
    cam = view.getCameraNode()

    if cam.getClassTypeId() != pCamClassTypeId():
        view.setCameraType("Perspective")
        util.printInfo("Set camera type to Perspective.")
        cam = view.getCameraNode()

    setCamera(camSettings.viewPoint, camSettings.direction, camSettings.upVector)
    util.printInfo("Camera type {}".format(view.getCameraType()))
    angle = degreeToRadians(camSettings.fieldOfView)
    util.printInfo("Setting the fieldOfView = {} radians ({}"\
            " degrees)".format(angle, camSettings.fieldOfView))
    cam.heightAngle.setValue(angle)


def setOCamera(camSettings: OrthogonalCamera):

    """ Sets the camera's position, orientation and viewToWorldScale to `camSettings`.

    If the camera in the current view is not a Orthographic camera, it is changed
    by calling View3DInventorPy.setCameraType("Orthographic").
    The view to world scale is set by setting the value `height` in
    SoOrthographicCamera.
    """

    view = FreeCADGui.ActiveDocument.ActiveView
    cam = view.getCameraNode()

    if cam.getClassTypeId() != oCamClassTypeId():
        view.setCameraType("Orthographic")
        util.printInfo("Set camera type to Orthographic.")
        cam = view.getCameraNode()

    setCamera(camSettings.viewPoint, camSettings.direction, camSettings.upVector)
    util.printInfo("Camera type {}".format(view.getCameraType()))
    cam.height.setValue(camSettings.viewWorldScale)


def drawLine(start: FreeCAD.Vector, end: FreeCAD.Vector):

    """ Creates a line from start to end using the draft workbench. """

    if start is None or end is None:
        return None
    if not (isinstance(start, FreeCAD.Vector) and isinstance(end,
            FreeCAD.Vector)):
        return None

    pl = FreeCAD.Placement()
    pl.Rotation.Q = (0, 0, 0, 1) # set the rotation in terms of quarternions
    pl.Base = copy.deepcopy(start)
    points = [start, end]
    line = Draft.makeWire(points, placement=pl, closed=False, face=False,
            support = None)

    return line


def checkIfGroupExists(name: str):

    obj = doc.getObject(name)
    if obj is None:
        return False

    if not isinstance(obj, FreeCAD.DocumentObjectGroup):
        return False

    return obj


def createLines(lines: List[Line]):

    """ Creates every line in `lines` and adds them to the BCF group

    Returns True if all lines could be created. Otherwise False is returned.
    """

    global bcfGroup
    global bcfGroupName

    # get a reference to the bcf group and store it in bcfGroup
    if bcfGroup is None:
        group = checkIfGroupExists(bcfGroupName)
        if not group:
            bcfGroup = doc.addObject("App::DocumentObjectGroup", bcfGroupName)
        else:
            bcfGroup = obj

    # try to add all lines in `lines`. Skip the failing ones
    for line in lines:
        start = line.start
        end = line.end
        fStart = FreeCAD.Vector(start.x, start.y, start.z)
        fEnd = FreeCAD.Vector(end.x, end.y, end.z)
        line = drawLine(fStart, fEnd)

        if line is not None:
            bcfGroup.addObject(line)
        else:
            util.printErr("Could not add line. Either start or end is None, or"\
                    " the points are not of type `FreeCAD.Vector`")

    return True


def createClippingPlane(clip: ClippingPlane):

    """ Creates a clipping plane `clip` on the scene graph of FreeCADGui """

    if (clip is None or
            clip.direction is None or
            clip.location is None):
        return False

    sceneGraph = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()

    # create plane that gets added to the scene graph
    normal = coin.SbVec3f(convertToFreeCADUnits(distance = clip.direction.x),
            convertToFreeCADUnits(distance = clip.direction.y),
            convertToFreeCADUnits(distance = clip.direction.z))
    ref = coin.SbVec3f(convertToFreeCADUnits(distance = clip.location.x),
            convertToFreeCADUnits(distance = clip.location.y),
            convertToFreeCADUnits(distance = clip.location.z))
    plane = coin.SbPlane(normal, ref)

    clipplane = coin.SoClipPlane()
    clipplane.plane.setValue(plane)

    # add the clipping plane to the scenegraph
    sceneGraph.insertChild(clipplane, 0)
    clipPlanes.append(clipplane)

    return True


def readCamera():

    """ Read the current settings of the camera and return a Camera object.

    The camera object returned will be an instance of either OrthogonalCamera or
    PerspectiveCamera, depending on the camera node in the view. For the
    perspective camera the property `heightAngle` is read from the view camera
    and interpreted as `fieldOfView`. For the orthogonal camera the property
    `height` is read and interpreted as view to world scale.
    If reading of the camera settings was unsuccessful then `None` is returned
    and a descriptive error message is printed.
    """

    view = FreeCADGui.ActiveDocument.ActiveView
    cam = view.getCameraNode()

    # translate freecads vector to a vector in the plugin
    fPosVec = cam.position.getValue()
    pPosVec = Point(fPosVec[0], fPosVec[1], fPosVec[2])

    fOrientMat = cam.orientation.getValue().getMatrix().getValue()
    fUpVec = fOrientMat[1][0:3]
    fDirVec = fOrientMat[2][0:3]
    pUpVec = Direction(fUpVec[0], fUpVec[1], fUpVec[2])
    pDirVec = Direction(fDirVec[0], fDirVec[1], fDirVec[2])

    vpCam = None # viewpoint camera settings
    classTypeId = cam.getClassTypeId
    if classTypeId() == pCamClassTypeId():
        fieldOfView = cam.heightAngle.getValue()
        vpCam = PerspectiveCamera(pPosVec, pDirVec, pUpVec, fieldOfView)

    elif classTypeId() == oCamClassTypeId():
        viewToWorldScale = cam.height.getValue()
        vpCam = OrthogonalCamera(pPosVec, pDirVec, pUpVec, viewToWorldScale)

    else:
        util.printErr("The current camera type is not known. Supported camera"\
                " types are: 'Perspective' and 'Orthographic'. Current type:"\
                " {}".format(type(pCam)))

    return vpCam


def getIfcObjects():

    """ Scans all objects in FreeCAD and returns a dictionary of Ifc objects.

    The criterion for an object to be an Ifc Object is to have the attribute
    `IfcData`, which is a dictionary; and this dictionary must have key value
    pair with the key "IfcUID".
    The dictionary returned will have keys corresponding to the IfcUIDs and the
    values will be the objects themselves.
    """

    doc = FreeCAD.ActiveDocument
    if doc is None:
        util.printErr("Compiling of a list of IfcObjects failed! No document"\
                " is currently open.")
        return None

    ifcObjects = dict()
    isIfcObject = lambda obj: hasattr(obj, "IfcData") and "IfcUID" in obj.IfcData
    # walk through all freecad objects and check if they are ifc objects
    for fObj in doc.Objects:
        if isIfcObject(fObj):
            ifcObjects[fObj.IfcData["IfcUID"]] = fObj

    return ifcObjects


def colourToTuple(colour: str):

    """ Convert a html colour value to a tuple of three elements.

    A colour value is represented as floating point number between 1 and 0.
    It is assumed that the colour string is either 7 or 4 elements long,
    including the '#' character.
    """

    colourPattern = re.compile("^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    if not colourPattern.fullmatch(colour):
        return None

    maxColVal = 0xFF if len(colour) == 7 else 0xF

    rgbStr = colour[1:]
    rgbVal = []
    iterationStep = int(len(rgbStr) / 3)
    i = 0
    while i < (len(rgbStr) / iterationStep):
        startColVal = i*iterationStep
        endColVal = startColVal + iterationStep
        col = rgbStr[startColVal : endColVal]
        rgbVal.append(int(col, 16))
        i += 1

    return (rgbVal[0]/maxColVal, rgbVal[1]/maxColVal, rgbVal[2]/maxColVal)


def colourComponents(colourings: List[ComponentColour], ifcObjects = None):

    """ Set the colour of every object with a matching IfcUID.

    Returns the number of objects whose colours could be set (i.e.: the number
    of objects that were found with a IfcUID that matched an entry of
    `colourings`.
    """

    util.printInfo("Colouring components")

    if ifcObjects is None:
        ifcObjects = getIfcObjects()

    colouringCnt = 0
    for colouring in colourings:
        colour = colouring.colour
        colTuple = colourToTuple(colour)

        util.printInfo("Got colour {} for components {}".format(colTuple,
            colouring.components))
        for component in colouring.components:
            cIfcId = component.ifcId

            if cIfcId in ifcObjects:
                obj = ifcObjects[cIfcId]
                # view object
                vObj = obj.Document.getObject(obj.Name).ViewObject
                if hasattr(vObj, "ShapeColor"):
                    vObj.ShapeColor = colTuple
                    util.printInfo("Setting color of obj ({}) to"\
                            " {}".format(vObj, colTuple))


def applyVisibilitySettings(defaultVisibility: bool,
        exceptions: List[Component], ifcObjects = None):

    """ Set every object's visibility to `defaultVisibility` except for
    `exceptions`.

    All components listed in `exceptions` will be assigned the complement of
    `defaultVisibility`.
    """

    if ifcObjects is None:
        ifcObjects = getIfcObjects()

    if len(ifcObjects) == 0:
        return False

    # set visibility of all objects to `defaultVisibility`
    for obj in FreeCAD.ActiveDocument.Objects:
        obj.ViewObject.Visibility = defaultVisibility

    # set visibility of exceptions, if they are found by their ifcId, to the
    # complement of `defaultVisibility`
    for exception in exceptions:
        excId = exception.ifcId

        if excId in ifcObjects:
            ifcObjects[excId].ViewObject.Visibility = not defaultVisibility

    return True


def selectComponents(components: List[Component], ifcObjects = None):

    """ Selects every object that the same IfcUID as a component in `components`

    The current selection, if set, will be cleared before the components will be
    added to the selection.
    Returns the number of objects that are in the selection.
    """

    if ifcObjects is None:
        ifcObjects = getIfcObjects()

    util.printInfo("Walking through components {} to select".format(components))
    selectionCnt = 0
    FreeCADGui.Selection.clearSelection()
    for component in components:
        ifcUID = component.ifcId

        util.printInfo("Checking {} if it is in ifcObjects {}".format(ifcUID,
            ifcObjects))
        if ifcUID in ifcObjects:
            FreeCADGui.Selection.addSelection(ifcObjects[ifcUID])
            selectionCnt += 1
            util.printInfo("Adding object {} to"\
                    " selection.".format(ifcObjects[ifcUID]))

    return selectionCnt




