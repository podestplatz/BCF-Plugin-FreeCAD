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

import logging

import bcfplugin
import bcfplugin.rdwr.project as p

from copy import deepcopy
from enum import Enum
from datetime import datetime
from bcfplugin.rdwr.interfaces.hierarchy import Hierarchy
from bcfplugin.rdwr.interfaces.state import State
from bcfplugin.rdwr.interfaces.identifiable import Identifiable

logger = bcfplugin.createLogger(__name__)


class ModificationType(Enum):

    """ Enum defining the two types of modifications: creation and
    modification.

    This is used for the ModificationAuthor and ModificationDate classes, to
    let them represent both Author and Modified Author and Date and Modified
    Date types.
    """

    CREATION = 1
    MODIFICATION = 2


class ModificationAuthor(p.SimpleElement):

    """ Represents the XML type markup.xsd:UserIdType.

    But this class is also used to discern between the XML nodes "Author" and
    "ModifiedAuthor".
    """

    def __init__(self,
            author: str,
            containingElement = None,
            modType: ModificationType = ModificationType.CREATION,
            state: State.States = State.States.ORIGINAL):

        name = ""
        if modType == ModificationType.CREATION:
            name = "CreationAuthor"
        if modType == ModificationType.MODIFICATION:
            name = "ModifiedAuthor"
        p.SimpleElement.__init__(self, author, name, "", containingElement, state)


    def __deepcopy__(self, memo):

        cpysuper = p.SimpleElement.__deepcopy__(self, memo)
        cpy = ModificationAuthor(deepcopy(self.author))
        cpy.id = cpysuper.id
        cpy.state = cpysuper.state
        cpy.xmlName = cpysuper.xmlName
        cpy.defaultValue = cpysuper.defaultValue

        return cpy


    @property
    def author(self):
        return self.value

    @author.setter
    def author(self, newVal):
        if not isinstance(newVal, str):
            raise ValueError("Author has to be of type string, current type"\
                    " {}".format(type(newVal)))
        else:
            self.value = newVal


    def searchObject(self, object):

        if not issubclass(type(object), Identifiable):
            return None

        id = object.id
        if self.id == id:
            return self

        return None


class ModificationDate(p.SimpleElement):

    """ Represents the XML type datetime.

    But this class is also used to discern between the XML nodes "Date" and
    "ModifiedDate".
    """

    def __init__(self,
            date: datetime,
            containingElement = None,
            modType: ModificationType = ModificationType.CREATION,
            state: State.States = State.States.ORIGINAL,
            dateFormat = "%Y-%m-%d %X"
            ):

        name = ""
        if modType == ModificationType.CREATION:
            name = "CreationDate"
        if modType == ModificationType.MODIFICATION:
            name = "ModifiedDate"
        p.SimpleElement.__init__(self, date, name, None, containingElement, state)
        self.dateFormat = dateFormat


    def __str__(self):

        """ Returns a string representation of the set datetime.

        The format is YYYY-MM-DD hh:mm
        """

        ret_str = ""
        if self.value is not None:
            ret_str = self.value.strftime(self.dateFormat)
        else:
            ret_str = "Not set"

        return ret_str


    def __deepcopy__(self, memo):

        cpysuper = p.SimpleElement.__deepcopy__(self, memo)
        cpy = ModificationDate(deepcopy(self.date))
        cpy.id = cpysuper.id
        cpy.state = cpysuper.state
        cpy.xmlName = cpysuper.xmlName
        cpy.defaultValue = cpysuper.defaultValue

        return cpy


    @property
    def date(self):
        return self.value

    @date.setter
    def date(self, newVal):
        if not isinstance(newVal, datetime):
            raise ValueError("Date has to be of type datetime, current type"\
                    " {}".format(type(newVal)))
        else:
            self.value = newVal


    def getEtElement(self, elem):

        """
        Convert the contents of the object to an xml.etree.ElementTree.Element
        representation. `element` is the object of type xml.e...Tree.Element
        which shall be modified and returned.
        """

        elem.tag = self.xmlName
        elem.text = self.date.isoformat("T", "seconds")

        return elem


    def searchObject(self, object):

        if not issubclass(type(object), Identifiable):
            return None

        id = object.id
        if self.id == id:
            return self

        return None
