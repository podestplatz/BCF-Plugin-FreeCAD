class XMLName:

    """
    Every inheriting class should correspond to either a node in one xml file or
    an attribute of a node. The inherited property `xmlName` holds the name of
    the node/attribute. Every class that corresponds to a node is also expected
    to implement getEtElement() which serializes the contents of itself into a
    object of type xml.etree.ElementTree.Element.
    """

    def __init__(self, name = ""):
        if name == "":
            self._name = self.__class__.__name__
        else:
            self._name = name

    def __eq__(self, other):
        if other is None:
            return False

        if type(self) != type(other):
            return False

        return self._name == other.xmlName


    @property
    def xmlName(self):
        return self._name

    @xmlName.setter
    def xmlName(self, newVal):
        pass

    def getEtElement(self, elem):
        """
        Convert the contents of the object to an xml.etree.ElementTree.Element
        representation. `element` is the object of type xml.e...Tree.Element
        which shall be modified and returned.
        """

        raise NotImplementedError("The class inheriting should provide this method")
