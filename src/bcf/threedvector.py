class ThreeDVector:

    """
    General representation of a three dimensional vector which can be
    specialised to a point or a direction vector
    """

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.x == other.x and self.y == other.y and self.z == other.z


class Point(ThreeDVector):

    """ Represents a point in the three dimensional space """

    def __init__(self, x: float, y: float, z: float):
        super(Point, self).__init__(x, y, z)


class Direction(ThreeDVector):

    """ Represents a vector in the three dimensional space """

    def __init__(self, x: float, y: float, z: float):
        super(Direction, self).__init__(x, y, z)


class Line:

    """ Represents a line that goes throught the three dimensional space """

    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.start == other.start and self.end == other.end


class ClippingPlane:

    """ TODO: check out what for the clipping plane is used """

    def __init__(self, location: Point, direction: Direction):
        self.location = location
        self.direction = direction


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.location == other.location and
                self.direction == other.direction)

