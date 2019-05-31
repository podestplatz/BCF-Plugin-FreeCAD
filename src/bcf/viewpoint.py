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

        super(OrthogonalCamera, self).__init__(viewPoint, direction, upVector)
        self.viewWorldScale = viewWorldScale


class Component:

    def __init__(self,
            ifcId: UUID,
            originatingSystem: str = None,
            authoringtoolId: str = None):
        self.ifcId = ifcId
        self.originatingSystem = originatingSystem
        self.authoringtoolId = authoringtoolId


class ComponentColour:

    def __init__(self,
            colour: str,
            components: List[Component]): # has to have at least one element

        if len(components) == 0:
            raise InvalidArgumentException
        self.colour = colour
        self.components = components


class ViewSetupHints:

    def __init__(self, openingsVisible: bool = False,
            spacesVisible: bool = False,
            spaceBoundariesVisible: bool = False):

        self.openingsVisible = openingsVisible
        self.spaceBoundariesVisible = spaceBoundariesVisible
        self.spacesVisible = spacesVisible


class Components:

    def __init__(self,
            visibilityDefault: bool,
            visibilityExceptions: List[Component],
            selection: List[Component] = list(),
            viewSetupHints: ViewSetupHints = None,
            colouring: List[ComponentColour] = list()):
        self.viewSetuphints = viewSetupHints
        self.selection = selection
        self.visibilityDefault = visibilityDefault
        self.visibilityExceptions = visibilityExceptions
        self.colouring = colouring


class Viewpoint:

    """ """

    def __init__(self,
            id: UUID,
            components: Components = None,
            oCamera: OrthogonalCamera = None,
            pCamera: PerspectiveCamera = None,
            lines: List[Line] = list(),
            clippingPlanes: List[ClippingPlane] = list(),
            bitmaps: List[Bitmap] = list()):

        self.id = id
        self.components = components
        self.oCamera = oCamera
        self.pCamera = pCamera
        self.lines = lines
        self.clippingPlanes = clippingPlanes
        self.bitmaps = bitmaps
