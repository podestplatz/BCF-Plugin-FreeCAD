from enum import Enum
from datetime import datetime
from interfaces.hierarchy import Hierarchy
from interfaces.state import State
from interfaces.identifiable import Identifiable

import bcf.project as p


class ModificationType(Enum):
    CREATION = 1
    MODIFICATION = 2

class ModificationAuthor(p.SimpleElement):

    """ Holds the value of an `Author` xml element.

    This class represents two kinds of xml elements. CreationAuthor and
    ModifiedAuthor. To report the correct name a differentiation at creation is
    done and self.name properly set.
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


    @property
    def author(self):
        return self.value

    @author.setter
    def author(self, newVal):
        p.debug("set author to {}".format(newVal))
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

    """ Holds the value of an `Date` xml element.

    This class represents two kinds of xml elements. CreationDate and
    ModifiedDate. To report the correct name a differentiation at creation is
    done and self.name properly set.
    """

    def __init__(self,
            date: datetime,
            containingElement = None,
            modType: ModificationType = ModificationType.CREATION,
            state: State.States = State.States.ORIGINAL):

        name = ""
        if modType == ModificationType.CREATION:
            name = "CreationDate"
        if modType == ModificationType.MODIFICATION:
            name = "ModifiedDate"
        p.SimpleElement.__init__(self, date, name, None, containingElement, state)


    @property
    def date(self):
        return self.value

    @date.setter
    def date(self, newVal):
        p.debug("set date to {}".format(newVal))
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
