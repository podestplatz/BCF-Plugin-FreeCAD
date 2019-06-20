from enum import Enum
from typing import List, Dict
from uuid import UUID
from bcf.threedvector import *
from bcf.project import listSetContainingElement
from interfaces.hierarchy import Hierarchy
from interfaces.state import State
from interfaces.xmlname import XMLName
from interfaces.identifiable import Identifiable


class BitmapFormat(Enum):
    JPG = 1
    PNG = 2


class Bitmap(Hierarchy, State, XMLName):

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
            height: float,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function of Bitmap """

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.format = format
        self.reference = reference
        self.location = location
        self.normal = normal
        self.upVector = upVector
        self.height = height

        # set containingObject of complex members
        if self.location is not None:
            self.location.containingObject = self
        if self.normal is not None:
            self.normal.containingObject = self
        if self.upVector is not None:
            self.upVector.containingObject = self


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


    def getEtElement(self, elem):

        elem.tag = self.xmlName

        formatElem = ET.SubElement(elem, "Format")
        formatElem.text = self.format.name

        referenceElem = ET.SubElement(elem, "Reference")
        referenceElem.text = self.reference

        locationElem = ET.SubElement(elem, "Location")
        locationElem = self.location.getEtElement(locationElem)

        normalElem = ET.SubElement(elem, "Normal")
        normalElem = self.normal.getEtElement(normalElem)

        upElem = ET.SubElement(elem, "Up")
        upElem = self.upVector.getEtElement(upElem)

        heightElem = ET.SubElement(elem, "Height")
        heightElem.text = str(self.height)

        return elem


class Camera(Hierarchy, State, XMLName):

    """ Base class of PerspectiveCamera and OrthogonalCamera """

    def __init__(self,
            viewPoint: Point,
            direction: Direction,
            upVector: Direction,
            containingElement = None,
            state: State.States = State.States.ORIGINAL,
            xmlName: str = ""):

        """ Initialisation function of Camera """

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self, xmlName)
        self.viewPoint = viewPoint
        self.direction = direction
        self.upVector = upVector

        # set containingObject of complex members
        if self.viewPoint is not None:
            self.viewPoint.containingObject = self
        if self.direction is not None:
            self.direction.containingObject = self
        if self.upVector is not None:
            self.upVector.containingObject = self


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.viewPoint == other.viewPoint and
                self.direction == other.direction and
                self.upVector == other.upVector)


    def getEtElement(self, elem):

        elem.tag = self.xmlName

        cViewpointElem = ET.SubElement(elem, "CameraViewPoint")
        cViewpointElem = self.viewPoint.getEtElement(cViewpointElem)

        cDirectionElem = ET.SubElement(elem, "CameraDirection")
        cDirectionElem = self.direction.getEtElement(cDirectionElem)

        cUpVector = ET.SubElement(elem, "CameraUpVector")
        cUpVector = self.upVector.getEtElement(cUpVector)

        return elem


class PerspectiveCamera(Camera, XMLName):

    """ """

    def __init__(self,
            viewPoint: Point,
            direction: Direction,
            upVector: Direction,
            fieldOfView: int,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):
        Camera.__init__(self,
                viewPoint,
                direction,
                upVector,
                containingElement,
                state,
                self.__class__.__name__)
        self.fieldOfView = fieldOfView


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """
        superEqual = super(PerspectiveCamera, self).__eq__(other)
        if (superEqual and type(self) == type(other)):
            return self.fieldOfView == other.fieldOfView
        return False


    def getEtElement(self, elem):

        elem = Camera.getEtElement(self, elem)

        fieldOfViewElem = ET.SubElement(elem, "FieldOfView")
        fieldOfViewElem.text = str(self.fieldOfView)

        return elem


class OrthogonalCamera(Camera, XMLName):

    """ """

    def __init__(self,
            viewPoint: Point,
            direction: Direction,
            upVector: Direction,
            viewWorldScale: int,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function of OrthogonalCamera """

        Camera.__init__(self,
                viewPoint,
                direction,
                upVector,
                containingElement,
                state)
        XMLName.__init__(self)
        self.viewWorldScale = viewWorldScale


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        superEqual = super(OrthogonalCamera, self).__eq__(other)
        if (superEqual and type(self) == type(other)):
            return self.viewWorldScale == other.viewWorldScale
        return False


    def getEtElement(self, elem):

        elem = Camera.getEtElement(self, elem)

        viewWorldScaleElem = ET.SubElement(elem, "ViewToWorldScale")
        viewWorldScaleElem.text = str(self.viewWorldScale)

        return elem


class Component(Hierarchy, State, XMLName):

    def __init__(self,
            ifcId: UUID = None,
            originatingSystem: str = "",
            authoringtoolId: str = "",
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
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


    def getEtElement(self, elem):

        elem.tag = self.xmlName

        if self.ifcId is not None:
            elem.attrib["IfcGuid"] = str(self.ifcId)

        if self.originatingSystem != "":
            origSysElem = ET.SubElement(elem, "OriginatingSystem")
            origSysElem.text = self.originatingSystem

        if self.authoringtoolId != "":
            authToolIdElem = ET.SubElement(elem, "AuthoringToolId")
            authToolIdElem.text = self.authoringtoolId

        return elem


class ComponentColour(Hierarchy, State, XMLName):

    def __init__(self,
            colour: str,
            components: List[Component], # has to have at least one element
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self, "Coloring")
        if len(components) == 0:
            raise ValueError("`components` has to have at least one element")
        self.colour = colour
        self.components = components

        # set containingObject of complex members
        listSetContainingElement(self.components, self)


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



class ViewSetupHints(Hierarchy, State, XMLName):

    def __init__(self, openingsVisible: bool = False,
            spacesVisible: bool = False,
            spaceBoundariesVisible: bool = False,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
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


    def getEtElement(self, elem):

        elem.tag = self.xmlName

        elem.attrib["SpacesVisible"] = str(self.spacesVisible).lower()
        elem.attrib["SpaceBoundariesVisible"] = str(self.spaceBoundariesVisible).lower()
        elem.attrib["OpeningsVisible"] = str(self.openingsVisible).lower()

        return elem


class Components(Hierarchy, State, XMLName):

    def __init__(self,
            visibilityDefault: bool,
            visibilityExceptions: List[Component],
            selection: List[Component] = list(),
            viewSetuphints: ViewSetupHints = None,
            colouring: List[ComponentColour] = list(),
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.viewSetuphints = viewSetuphints
        self.selection = selection
        self.visibilityDefault = visibilityDefault
        self.visibilityExceptions = visibilityExceptions
        self.colouring = colouring

        # set containingObject for complex members
        if self.viewSetuphints is not None:
            self.viewSetuphints.containingObject = self
        listSetContainingElement(self.selection, self)
        listSetContainingElement(self.colouring, self)
        listSetContainingElement(self.visibilityExceptions, self)

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


    def _generateComponentList(self, parent, compList):

        for component in compList:
            newComponent = ET.SubElement(parent, "Component")
            newComponent = component.getEtElement(newComponent)

        return parent


    def getEtElement(self, elem):

        elem.tag = self.xmlName

        if self.viewSetuphints is not None:
            viewSHElem = ET.SubElement(elem, "ViewSetupHints")
            viewSHElem = self.viewSetuphints.getEtElement(viewSHElem)

        if len(self.selection) > 0:
            selElem = ET.SubElement(elem, "Selection")
            selElem = self._generateComponentList(selElem, self.selection)

        visibilityElem = ET.SubElement(elem, "Visibility")
        exceptionsElem = ET.SubElement(visibilityElem, "Exceptions")
        exceptionsElem = self._generateComponentList(exceptionsElem,
                self.visibilityExceptions)

        if len(self.colouring) > 0:
            colouringElem = ET.SubElement(elem, "Coloring")
            for col in self.colouring:
                colourElem = ET.SubElement(elem, "Color")
                if col.colour != "":
                    colourElem.attrib["Color"] = col.colour

                colourElem = self._generateComponentList(colourElem,
                        col.components)

        return elem


class Viewpoint(Hierarchy, State, XMLName, Identifiable):

    """
    Viewpoint uses the default implementation of getStateList(). Objects of type
    Viewpoint are considered non-mutable, therefore the state
    State.States.MODIFIED is invalid for Viewpoint objects. Also resulting from
    the immutability is the fact that all members of Viewpoint are added and
    deleted with the viewpoint object.
    """

    def __init__(self,
            id: UUID,
            components: Components = None,
            oCamera: OrthogonalCamera = None,
            pCamera: PerspectiveCamera = None,
            lines: List[Line] = list(),
            clippingPlanes: List[ClippingPlane] = list(),
            bitmaps: List[Bitmap] = list(),
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self, "VisualizationInfo")
        Identifiable.__init__(self)
        self.xmlId = id
        self.components = components
        self.oCamera = oCamera
        self.pCamera = pCamera
        self.lines = lines
        self.clippingPlanes = clippingPlanes
        self.bitmaps = bitmaps

        # set containingObject for complex members
        if self.components is not None:
            self.components.containingObject = self
        if self.oCamera is not None:
            self.oCamera.containingObject = self
        if self.pCamera is not None:
            self.pCamera.containingObject = self
        listSetContainingElement(self.lines, self)
        listSetContainingElement(self.bitmaps, self)
        listSetContainingElement(self.clippingPlanes, self)


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.xmlId == other.xmlId and
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
\tbitmaps='{}')""".format(self.xmlId, str(self.components), str(self.oCamera),
                str(self.pCamera), str(self.lines), str(self.clippingPlanes),
                str(self.bitmaps))
        return ret_str


    def _generateListElements(self, parent, l):

        for item in l:
            newElem = ET.SubElement(parent, item.xmlName)
            newElem = item.getEtElement(newElem)

        return parent


    def getEtElement(self, elem):

        elem.tag = self.xmlName
        elem.attrib["Guid"] = str(self.xmlId)

        if self.components is not None:
            componentsElem = ET.SubElement(elem, "Components")
            componentsElem = self.components.getEtElement(componentsElem)

        if self.oCamera is not None:
            oCameraElem = ET.SubElement(elem, "OrthogonalCamera")
            oCameraElem = self.oCamera.getEtElement(oCameraElem)

        if self.pCamera is not None:
            pCameraElem = ET.SubElement(elem, "PerspectiveCamera")
            pCameraElem = self.pCamera.getEtElement(pCameraElem)

        if len(self.lines) > 0:
            linesElem = ET.SubElement(elem, "Lines")
            linesElem = self._generateListElements(linesElem, self.lines)

        if len(self.clippingPlanes) > 0:
            clippingPlanesElem = ET.SubElement(elem, "ClippingPlanes")
            clippingPlanesElem = self._generateListElements(clippingPlanesElem,
                    self.clippingPlanes)

        if len(self.bitmaps) > 0:
            self._generateListElements(elem, self.bitmaps)

        return elem
