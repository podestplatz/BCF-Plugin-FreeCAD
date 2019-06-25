class Hierarchy:

    """
    Every class implementing Hierarchy gets the member containingObject. This
    shall reference the object that hierarchically preceeds the object itself.
    """

    def __init__(self, containingObject=None):
        self.containingObject = containingObject


    def __eq__(self, other):
        if other is None:
            return False

        if type(self) != type(other):
            return False

        return self.containingObject == other.containingObject


    def getHierarchyList(self):

        """ Uses `containingObject` to create a list of parents.

        Thereby is the parent of an object A an object B if it holds a
        reference to A. This is true in most cases. Exceptions are objects of
        Comment. These might hold a reference to an object of type
        `ViewpointReference`, but they are not parent of such.

        The first element of the list is the self and the last element in
        the list is the one whose `containingObject == None`
        """

        currentObject = self
        hierarchy = [ currentObject ]
        while currentObject:
            if currentObject.containingObject:
                currentObject = currentObject.containingObject
                hierarchy.append(currentObject)
            else:
                currentObject = None

        return hierarchy


    @staticmethod
    def checkAndGetHierarchy(element):

        """ Wrapper method for getHierarchyList.

        Creates a hierarchy list starting from `element`.
        """

        if not isinstance(element, Hierarchy):
            return None
        return element.getHierarchyList()
