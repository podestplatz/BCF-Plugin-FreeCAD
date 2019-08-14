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

        if not issubclass(type(element), Hierarchy):
            return None
        return element.getHierarchyList()
