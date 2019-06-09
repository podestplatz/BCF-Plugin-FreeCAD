class XMLName:
    def __init__(self, name = ""):
        if name == "":
            self._name = self.__class__.__name__
        else:
            self._name = name

    @property
    def xmlName(self):
        return self._name

    @xmlName.setter
    def xmlName(self, newVal):
        pass

    def getEtElement(self, element):
        """
        Convert the contents of the object to an xml.etree.ElementTree.Element
        representation. `element` is the object of type xml.e...Tree.Element
        which shall be modified and returned.
        """
        pass
