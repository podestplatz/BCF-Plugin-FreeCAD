from uuid import UUID
from bcf.uri import Uri
from interfaces.hierarchy import Hierarchy
from interfaces.state import State
from interfaces.xmlname import XMLName
from interfaces.identifiable import XMLIdentifiable, Identifiable

DEBUG = False

if DEBUG:
    import inspect

def debug(msg):
    if DEBUG:
        callerName = inspect.stack()[1].function
        print("[DEBUG]{}(): {}".format(callerName, msg))


def listSetContainingElement(itemList, containingObject):
    if len(itemList) == 0:
        return None

    for item in itemList:
        if not issubclass(type(item), Hierarchy):
            raise ValueError("{} is not a subclass of Hierarchy! Element of"\
                    " the wrong type has index {}".format(type(item),
                        itemList.index(item)))

    for item in itemList:
        item.containingObject = containingObject


def searchListObject(object, elementList):

    if not issubclass(type(object), Identifiable):
        return None

    searchResult = None
    for item in elementList:
        if item is None:
            continue

        searchResult = item.searchObject(object)
        if searchResult is not None:
            break

    return searchResult


class SimpleElement(XMLName, Hierarchy, State, Identifiable):

    """
    Used for representing elements that are defined to be simple elements
    in the corresponding xsd file
    """

    def __init__(self, value, xmlName, containingElement,
            state = State.States.ORIGINAL):
        XMLName.__init__(self, xmlName)
        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        Identifiable.__init__(self)
        self.value = value


    def __eq__(self, other):
        if type(self) != type(other):
            return False

        # None != None is assumed
        if self is None or other is None:
            return False

        return (self.value == other.value and
                self.xmlName == other.xmlName)


    def __str__(self):
        return "{}: {}".format(self.xmlName, self.value)


    def getEtElement(self, elem):

        """
        Default implementation for simple elements. Constructs an ET.Element
        with the tag equal to `xmlName` and pastes `value` into the text section
        of the node
        """

        elem.tag = self.xmlName
        elem.text = str(self.value)

        return elem


    def searchObject(self, object):

        if not issubclass(type(object), Identifiable):
            return None

        id = object.id
        if self.id == id:
            return self
        else:
            return None


class SimpleList(list, XMLName, Hierarchy, State, Identifiable):

    """
    Used for lists that contain just simple types. For example the `Labels`
    element in Topic is translated to a list in this data model. Every `Label`
    element just contains a string (and therefore is a simple type).
    """

    def __init__(self, data=[], xmlName = "", containingElement = None,
            state = State.States.ORIGINAL):

        simpleElementList = list()
        for item in data:
            newSimpleElement = SimpleElement(item, xmlName, containingElement,
                    state)
            simpleElementList.append(newSimpleElement)

        list.__init__(self, simpleElementList)
        XMLName.__init__(self, xmlName)
        State.__init__(self, state)
        Hierarchy.__init__(self, containingElement)
        Identifiable.__init__(self)


    def append(self, item):

        """
        Envelope every type that is not of instance SimpleElement into an object
        of simple element, with the default values of the class object itself
        (xmlname, containintObject). The state is automatically set to
        state.State.States.ADDED
        """

        newElem = item
        if not isinstance(newElem, SimpleElement):
            newElem = SimpleElement(item, self.xmlName, self.containingObject,
                    self.States.ADDED)
        else:
            newElem.state = State.States.ADDED

        list.append(self, newElem)


    def __eq__(self, other):

        return (list.__eq__(self, other) and
                XMLName.__eq__(self, other))


class Attribute(XMLName, Hierarchy, State, Identifiable):

    """
    Analogously to `SimpleElement` this class is used to represent attributes.
    """

    def __init__(self, value, xmlName, containingElement,
            state = State.States.ORIGINAL):
        XMLName.__init__(self, xmlName)
        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        Identifiable.__init__(self)
        self.value = value


    def searchObject(self, object):

        if not issubclass(type(object), Identifiable):
            return None

        id = object.id
        if self.id == id:
            return self
        else:
            return None


class Project(Hierarchy, State, XMLName, XMLIdentifiable, Identifiable):
    def __init__(self,
            uuid: UUID,
            name: str = "",
            extSchemaSrc: Uri = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function of Project """

        Hierarchy.__init__(self, None) # Project is the topmost element
        State.__init__(self, state)
        XMLName.__init__(self)
        XMLIdentifiable.__init__(self, uuid)
        Identifiable.__init__(self)
        self._name = SimpleElement(name, "Name", self)
        self._extSchemaSrc = SimpleElement(extSchemaSrc, "ExtensionSchema", self)
        self.topicList = list()

    @property
    def name(self):
        return self._name.value

    @name.setter
    def name(self, newVal):
        self._name.value = newVal

    @property
    def extSchemaSrc(self):
        return self._extSchemaSrc.value

    @extSchemaSrc.setter
    def extSchemaSrc(self, newVal):
        self._extSchemaSrc.value = newVal


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if type(self) != type(other):
            return False

        return self.xmlId == other.xmlId \
            and self.name == other.name \
            and self.extSchemaSrc == other.extSchemaSrc \
            and self.topicList == other.topicList


    def __str__(self):

        ret_str = """Project(
id='{}',
name='{}',
extSchemaSrc='{}',
topicList='{}')""".format(str(self.xmlId),
                str(self.name),
                str(self.extSchemaSrc),
                self.topicList)
        return ret_str


    def getStateList(self):

        stateList = list()
        if not self.isOriginal():
            stateList.append((self.state, self))

        stateList += self._name.getStateList()
        stateList += self._extSchemaSrc.getStateList()

        for markup in self.topicList:
            stateList += markup.getStateList()

        return stateList


    def searchObject(self, object):

        """
        Checks whether the current object has the id equal to `id`. If so it is
        returned. If not the members of the object are checked against `id`.
        Thereby implementing a depth first search.
        """

        if not issubclass(type(object), Identifiable):
            return None

        id = object.id
        if self.id == id:
            return self

        members = [self._name, self._extSchemaSrc]
        searchResult = searchListObject(object, members)
        if searchResult is not None:
            return searchResult

        searchResult = searchListObject(object, self.topicList)
        if searchResult is not None:
            return searchResult

        return None
