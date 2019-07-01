import rdwr.threedvector as vector
from pivy import coin
from util import debug, printErr, printInfo, FREECAD, GUI

if GUI and FREECAD:
    import FreeCADGui
    import FreeCAD

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

