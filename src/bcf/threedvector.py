class ThreeDVector:

    """
    General representation of a three dimensional vector which can be
    specialised to a point or a direction vector
    """

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

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

class ClippingPlane:

    """ TODO: check out what for the clipping plane is used """

    def __init__(self, location: Point, direction: Direction):
        self.location = location
        self.direction = direction
