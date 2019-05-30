from enum import Enum
from typing import List, Dict
from markup import ViewpointReference
from uuid import UUID
from threedvector import *

class BitmapFormat(Enum): #TODO integrate it with SchemaConstraint
    JPG = 1
    PNG = 2

class Bitmap:

    """
    Represents a bitmap, to which the according file is stored inside the
    topic folder
    """

    def __init__(self,
            format: BitmapFormat,
            reference: str, # name of the bitmap file in the topic folder
            location: Point,
            normal: Direction,
            upVector: Direction,
            height: float):

        """ Initialisation function of Bitmap """

        self.format = format
        self.reference = reference
        self.location = location
        self.normal = normal
        self.upVector = upVector
        self.height = height

class Camera:

    """ Base class of PerspectiveCamera and OrthogonalCamera """

    def __init__(self,
            viewPoint: Point,
            direction: Direction,
            upVector: Direction):

        """ Initialisation function of Camera """

        self.viewPoint = viewPoint
        self.direction = direction
        self.upVector = upVector

class PerspectiveCamera(Camera):

    """ """

    def __init__(self,
            viewPoint: Point,
            direction: Direction,
            upVector: Direction,
            fieldOfView: int):
        super(PerspectiveCamera, self).__init__(viewPoint, direction, upVector)
        self.fieldOfView = fieldOfView

class OrthogonalCamera(Camera):

    """ """

    def __init__(self,
            viewPoint: Point,
            direction: Direction,
            upVector: Direction,
            viewWorldScale: int):

        """ Initialisation function of OrthogonalCamera """

        super(PerspectiveCamera, self).__init__(viewPoint, direction, upVector)
        self.viewWorldScale = viewWorldScale


class Component:

    def __init__(self,
            ifcId: UUID,
            originatingSystem: str = None,
            authoringtoolId: str = None):
        self.ifcId = ifcId
        self.originatingSystem = originatingSystem
        self.authoringtoolId = authoringtoolId


class ComponentColor:

    def __init__(self,
            color: str,
            components: List[UUID]): # has to have at least one element

        if len(components) == 0:
            raise InvalidArgumentException
        self.color = color
        self.components = components


class Components:

    def __init__(self,
            visibilityDefault: bool,
            visibilityExceptions: List[Component],
            selection: List[Component] = list(),
            viewSetupHints: Dict = dict(),
            coloring: List[ComponentColor] = list()):
        self.viewSetuphints = viewSetuphints
        self.selection = selection
        self.visibilityDefault = visibilityDefault
        self.visibilityExceptions = visibilityExceptions
        self.coloring = coloring


class Viewpoint(ViewpointReference):

    """ """

    def __init__(self,
            id: UUID = None,
            components: Components = None, #TODO: define class
            camSetting: Camera = None,
            camSetting2: Camera = None,
            lines: List[Line] = list(),
            clippingPlanes: List[ClippingPlane] = list(),
            bitmaps: Bitmap = None):
        self.id = id
        self.components = components
        self.camSetting = camSetting
        self.camSetting2 = camSetting2
        self.lines = lines
        self.clippingPlanes = clippingPlanes
        self.bitmaps = bitmaps
