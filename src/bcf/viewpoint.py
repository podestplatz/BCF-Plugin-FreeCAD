import bcf.reader as reader
from enum import Enum
from typing import List, Dict
from uuid import UUID
from bcf.markup import ViewpointReference
from bcf.threedvector import *


class BitmapFormat(Enum):
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


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.format == other.format and
                self.reference == other.reference and
                self.location == other.location and
                self.normal == other.normal and
                self.upVector == other.upVector and
                self.height == other.height)


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


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.viewPoint == other.viewPoint and
                self.direction == other.direction and
                self.upVector == other.upVector)


class PerspectiveCamera(Camera):

    """ """

    def __init__(self,
            viewPoint: Point,
            direction: Direction,
            upVector: Direction,
            fieldOfView: int):
        super(PerspectiveCamera, self).__init__(viewPoint, direction, upVector)
        self.fieldOfView = fieldOfView


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """
        superEqual = super(PerspectiveCamera, self).__eq__(other)
        if (superEqual and type(self) == type(other)):
            return self.fieldOfView == other.fieldOfView
        return False


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


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        superEqual = super(OrthogonalCamera, self).__eq__(other)
        if (superEqual and type(self) == type(other)):
            return self.viewWorldScale == other.viewWorldScale
        return False


class Component:

    def __init__(self,
            ifcId: UUID,
            originatingSystem: str = "",
            authoringtoolId: str = ""):
        self.ifcId = ifcId
        self.originatingSystem = originatingSystem
        self.authoringtoolId = authoringtoolId


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.ifcId == other.ifcId and
                self.originatingSystem == other.originatingSystem and
                self.authoringtoolId == other.authoringtoolId)


    def __str__(self):

        ret_str = ("Component(ifcId='{}', originatingSystem='{}',"\
                " authoringToolId='{}')").format(self.ifcId,
                        self.originatingSystem, self.authoringtoolId)
        return ret_str



class ComponentColour:

    def __init__(self,
            colour: str,
            components: List[Component]): # has to have at least one element

        if len(components) == 0:
            raise ValueError("`components` has to have at least one element")
        self.colour = colour
        self.components = components


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.colour == other.colour and
                self.components == other.components)


    def __str__(self):

        ret_str = "ComponentColor(colour='{}',\n\t\tcomponents={})".format(
                self.colour, self.components)
        return ret_str



class ViewSetupHints:

    def __init__(self, openingsVisible: bool = False,
            spacesVisible: bool = False,
            spaceBoundariesVisible: bool = False):

        self.openingsVisible = openingsVisible
        self.spaceBoundariesVisible = spaceBoundariesVisible
        self.spacesVisible = spacesVisible


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.openingsVisible == other.openingsVisible and
                self.spaceBoundariesVisible == other.spaceBoundariesVisible and
                self.spacesVisible == other.spacesVisible)



class Components:

    def __init__(self,
            visibilityDefault: bool,
            visibilityExceptions: List[Component],
            selection: List[Component] = list(),
            viewSetuphints: ViewSetupHints = None,
            colouring: List[ComponentColour] = list()):

        self.viewSetuphints = viewSetuphints
        self.selection = selection
        self.visibilityDefault = visibilityDefault
        self.visibilityExceptions = visibilityExceptions
        self.colouring = colouring


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.viewSetuphints == other.viewSetuphints and
                self.selection == other.selection and
                self.visibilityDefault == other.visibilityDefault and
                self.visibilityExceptions == other.visibilityExceptions and
                self.colouring == other.colouring)


    def __str__(self):

        visibilityExcStr = [ str(exc) for exc in self.visibilityExceptions ]
        selectionStr = [ str(sel) for sel in self.selection ]
        ret_str = """Components(visibilityDefault='{}',
        visibilityExceptions='{}',
        selection='{}',
        viewSetupHints='{}',
        colouring='{}')""".format(self.visibilityDefault,
                visibilityExcStr, selectionStr,
                str(self.viewSetuphints), str(self.colouring))
        return ret_str


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


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if reader.DEBUG:
            if self.id != other.id:
                print("Viewpoint: id is different {}\n{}".format(self.id,
                    other.id))

            if self.components != other.components:
                print("Viewpoint: components is different\n{}\n{}".format(
                    self.components, other.components))

            if self.oCamera != other.oCamera:
                print("Viewpoint: oCamera is different {}\n{}".format(
                    self.oCamera, other.oCamera))

            if self.pCamera != other.pCamera:
                print("Viewpoint: pCamera is different {}\n{}".format(
                    self.pCamera, other.pCamera))

            if self.lines != other.lines:
                print("Viewpoint: lines are different {}\n{}".format(
                    self.lines, other.lines))

            if self.clippingPlanes != other.clippingPlanes:
                print("Viewpoint: clippingPlanes are different {}\n{}".format(
                    self.clippingPlanes, other.clippingPlanes))

            if self.bitmaps != other.bitmaps:
                print("Viewpoint: bitmaps are different {}\n{}".format(
                    self.bitmaps, other.bitmaps))

        return (self.id == other.id and
                self.components == other.components and
                self.oCamera == other.oCamera and
                self.pCamera == other.pCamera and
                self.lines == other.lines and
                self.clippingPlanes == other.clippingPlanes and
                self.bitmaps == other.bitmaps)


    def __str__(self):
        ret_str = """Viewpoint(
\tID='{}',
\tcomponents='{}',
\toCamera='{}',
\tpCamera='{}',
\tlines='{}',
\tclippingPlanes='{}',
\tbitmaps='{}')""".format(self.id, str(self.components), str(self.oCamera),
                str(self.pCamera), str(self.lines), str(self.clippingPlanes),
                str(self.bitmaps))
        return ret_str
