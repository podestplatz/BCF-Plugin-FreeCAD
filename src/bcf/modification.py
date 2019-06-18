from enum import Enum
from datetime import datetime
from interfaces.hierarchy import Hierarchy
from interfaces.state import State

import bcf.project as p


class ModificationType(Enum):
    CREATION = 1
    MODIFICATION = 2

class ModificationAuthor(p.SimpleElement):

    def __init__(self,
            author: str,
            containingElement = None,
            modType: ModificationType = ModificationType.CREATION,
            state: State.States = State.States.ORIGINAL):

        name = ""
        if modType == ModificationType.CREATION:
            name = "Author"
        if modType == ModificationType.MODIFICATION:
            name = "ModifiedAuthor"
        p.SimpleElement.__init__(self, author, name, containingElement, state)


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


class ModificationDate(p.SimpleElement):

    def __init__(self,
            date: datetime,
            containingElement = None,
            modType: ModificationType = ModificationType.CREATION,
            state: State.States = State.States.ORIGINAL):

        name = ""
        if modType == ModificationType.CREATION:
            name = "Date"
        if modType == ModificationType.MODIFICATION:
            name = "ModifiedDate"
        p.SimpleElement.__init__(self, date, name, containingElement, state)


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

        elem.tag = self.xmlName
        elem.text = self.date.isoformat("T", "seconds")

        return elem


class Modification(Hierarchy, State):

    """
    This class is used by Topic and Comment to for one denote the author
    and date of the last change and the creator and the creation date of an
    object of one of the respective classes.
    If it shall be written by the writer module then just supply it with
    self._author or self._date, not the object of Modification itself
    """

    def __init__(self,
            author: str,
            date: datetime,
            containingElement = None,
            state: State.States = State.States.ORIGINAL,
            modType: ModificationType = ModificationType.CREATION):

        """ Initialisation function for Modification """

        State.__init__(self, state)
        Hierarchy.__init__(self, containingElement)
        if modType == ModificationType.CREATION:
            self._author = p.SimpleElement(author, "Author", self)
            self._date = p.SimpleElement(date, "Date", self)
        else:
            self._author = p.SimpleElement(author, "ModifiedAuthor", self)
            self._date = p.SimpleElement(date, "ModifiedDate", self)

        # hacky way of pretending that author and date inherit XMLName
        # completely.
        self._author.getEtElement = self.getEtElementAuthor
        self._date.getEtElement = self.getEtElementDate


    @property
    def author(self):
        return self._author.value

    @author.setter
    def author(self, newVal):
        if not isinstance(newVal, str):
            raise ValueError("The value of author must be a string!")
        else:
            self._author.value = newVal

    @property
    def date(self):
        return self._date.value

    @date.setter
    def date(self, newValue):
        if not isinstance(newValue, datetime):
            raise ValueError("The value of date has to be datetime!")
        else:
            self._date.value = newVal


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.author == other.author and self.date == other.date


    def __str__(self):

        ret_str = "Modification(author='{}', datetime='{}')".format(self.author,
                self.date)
        return ret_str


    def getEtElementDate(self, elem):

        elem.tag = self._date.xmlName
        elem.text = self.date.isoformat("T", "seconds")

        return elem


    def getEtElementAuthor(self, elem):

        elem.tag = self._author.xmlName
        elem.text = self.author

        return elem
