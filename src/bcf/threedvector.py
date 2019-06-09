from interfaces.hierarchy import Hierarchy
from interfaces.state import State
from interfaces.xmlname import XMLName


class ThreeDVector(Hierarchy, State):

    """
    General representation of a three dimensional vector which can be
    specialised to a point or a direction vector
    """

    def __init__(self,
            x: float,
            y: float,
            z: float,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        self.x = x
        self.y = y
        self.z = z


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.x == other.x and self.y == other.y and self.z == other.z


class Point(ThreeDVector, XMLName):

    """ Represents a point in the three dimensional space """

    def __init__(self,
            x: float,
            y: float,
            z: float,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        ThreeDVector.__init__(self, x, y, z, containingElement, state)
        XMLName.__init__(self)


class Direction(ThreeDVector, XMLName):

    """ Represents a vector in the three dimensional space """

    def __init__(self,
            x: float,
            y: float,
            z: float,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        ThreeDVector.__init__(self, x, y, z, containingElement, state)
        XMLName.__init__(self)


class Line(Hierarchy, State, XMLName):

    """ Represents a line that goes throught the three dimensional space """

    def __init__(self,
            start: Point,
            end: Point,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.start = start
        self.end = end


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.start == other.start and self.end == other.end


class ClippingPlane(Hierarchy, State, XMLName):

    def __init__(self,
            location: Point,
            direction: Direction,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.location = location
        self.direction = direction


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.location == other.location and
                self.direction == other.direction)

