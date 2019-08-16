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

"""
Author: Patrick Podest
Date: 2019-08-16
Github: @podestplatz

**** Description ****
This file just provides the class Uri, which serves as wrapper for a string
that is thought of as a Uri. Currently no checks are done on the syntax level.
"""

from copy import deepcopy
from bcfplugin.rdwr.interfaces.hierarchy import Hierarchy
from bcfplugin.rdwr.interfaces.state import State
from bcfplugin.rdwr.interfaces.identifiable import Identifiable

class Uri(Hierarchy, State, Identifiable):

    """ This class wraps around strings representing a URI.

    No checks are done, though.
    """

    def __init__(self,
            uri: str,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        Identifiable.__init__(self)
        self.uri = uri

    def __deepcopy__(self, memo):

        """ Create a deepcopy of the object without copying `containingObject`
        """

        cpyid = deepcopy(self.id, memo)

        cpy = Uri(deepcopy(self.uri, memo))
        cpy.id = cpyid
        cpy.state = self.state

        return cpy


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if type(self) != type(other):
            return False

        return self.uri == other.uri

    def __str__(self):

        ret_str = "{}".format(self.uri)
        return ret_str


    def searchObject(self, object):

        if not issubclass(type(object), Identifiable):
            return None

        id = object.id
        if self.id == id:
            return self

        return None
