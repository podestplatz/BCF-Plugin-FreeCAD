"""
Copyright (C) 2019 PODEST Patrick

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

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
            self._xmlname = self.__class__.__name__
        else:
            self._xmlname = name

    def __eq__(self, other):
        if other is None:
            return False

        if type(self) != type(other):
            return False

        return self._xmlname == other.xmlName


    @property
    def xmlName(self):
        return self._xmlname

    @xmlName.setter
    def xmlName(self, newVal):
        self._xmlname = newVal

    def getEtElement(self, elem):

        """
        Convert the contents of the object to an xml.etree.ElementTree.Element
        representation. `element` is the object of type xml.e...Tree.Element
        which shall be modified and returned.
        """

        raise NotImplementedError("No implementation of `getEtElement` for {} found."\
                " The class inheriting should provide this"\
                " method".format(type(self)))
