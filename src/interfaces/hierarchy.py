class Hierarchy:
    def __init__(self, containingObject=None):
        self.containingObject = containingObject


    def __eq__(self, other):
        if other is None:
            return False

        if type(self) != type(other):
            return False

        return self.containingObject == other.containingObject


    def getHierarchyList(self):
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
        if not isinstance(element, Hierarchy):
            return None
        return element.getHierarchyList()
