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

from enum import Enum

class State:
    class States(Enum):
        ORIGINAL = 1
        ADDED = 2
        DELETED = 3
        MODIFIED = 4

    def __init__(self, state=States.ORIGINAL):
        self.state = state


    def isOriginal(self)-> 'bool':
        return self.state == State.States.ORIGINAL


    def getStateList(self)-> 'List[Tuple[State, Object]]':

        """
        Every class implementing this function shall compile a list of tuples
        one list element for each member object. Each list element has as first
        tuple element the state of the object
        (state.State.States.[ADDED|DELETED|MODIFIED|ORIGINAL]) and as second
        element the object itself.
        """
        stateList = list()
        if not self.isOriginal():
            stateList.append((self.state, self))

        return stateList

