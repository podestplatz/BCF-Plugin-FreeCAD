import re
from pivy import coin
from rdwr.viewpoint import OrthogonalCamera, PerspectiveCamera, Component
from rdwr.threedvector import Point, Direction

import rdwr.threedvector as vector
import util

# it is assumed that this file is only imported iff the plugin is running inside
# FreeCAD in Gui mode.
import FreeCADGui
import FreeCAD


pCamClassTypeId = coin.SoPerspectiveCamera_getClassTypeId
oCamClassTypeId = coin.SoOrthographicCamera_getClassTypeId


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

    setCamera(camSettings.viewPoint, camSettings.direction, camSettings.upVector)
    cam.heightAngle.setValue(camSettings.fieldOfView)


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

    setCamera(camSettings.viewPoint, camSettings.direction, camSettings.upVector)
    cam.height.setValue(camSettings.viewWorldScale)


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

    colourPattern = re.compile("^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    if not colourPattern.fullmatch(colour):
        return None

    maxColVal = 255.0 if len(colour) == 7 else 16.0

    rgbStr = colour[1:]
    rgbVal = []
    iterationStep = len(rgbStr)/2 # integer division
    i = 0
    while i < len(rgbStr):
        startColVal = i*iterationStep
        endColVal = startColVal + iterationStep
        col = rgbStr[startColVal : endColVal]

    rgbInt = [ int(rgbStr[0], 16),
            int(rgbStr[1], 16),
            int(rgbStr[2], 16) ]

    return (rgbInt[0]/maxColVal, rgbInt[1]/maxColVal, rgbInt[2]/maxColVal)



def colourComponents(colourings: List[ComponentColour], ifcObjects = None):

    """ Set the colour of every object with a matching IfcUID.

    Returns the number of objects whose colours could be set (i.e.: the number
    of objects that were found with a IfcUID that matched an entry of
    `colourings`.
    """

    if ifcObjects is None:
        ifcObjects = getIfcObjects()

    colouringCnt = 0
    for colouring in colourings:
        colour = colouring.colour


def selectComponents(components: List[Component], ifcObjects = None):

    """ Selects every object that the same IfcUID as a component in `components`

    The current selection, if set, will be cleared before the components will be
    added to the selection.
    Returns the number of objects that are in the selection.
    """

    if ifcObjects is None:
        ifcObjects = getIfcObjects()

    selectionCnt = 0
    FreeCADGui.Selection.clearSelection()
    for component in components:
        ifcUID = component.ifcId

        if ifcUID in ifcObjects:
            FreeCADGui.Selection.addSelection(ifcObjects[ifcUID])
            selectionCnt += 1

    return selectionCnt




