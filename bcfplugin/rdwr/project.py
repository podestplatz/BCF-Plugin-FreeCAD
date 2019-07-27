from uuid import UUID
from util import debug
from rdwr.uri import Uri
from rdwr.interfaces.hierarchy import Hierarchy
from rdwr.interfaces.state import State
from rdwr.interfaces.xmlname import XMLName
from rdwr.interfaces.identifiable import XMLIdentifiable, Identifiable


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

    typeDict = { "int": int, "float": float, "str": str }

    def __init__(self, value, xmlName, defaultValue, containingElement,
            state = State.States.ORIGINAL):
        XMLName.__init__(self, xmlName)
        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        Identifiable.__init__(self)
        self._value = value
        self.defaultValue = defaultValue


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

    @property
    def value(self):
        return self._value


    @value.setter
    def value(self, newValue):

        """ Try to convert the value automatically to the type of the default
        value.

        For example:
            `newValue` is of type str, `self.defaultValue` is of type
            int then the second line resolves to:
                self._value = int(newValue)
        """

        dstClassName = self.defaultValue.__class__.__name__
        if dstClassName in self.typeDict:
            self._value = self.typeDict[dstClassName](newValue)
        else:
            self._value = newValue


    def getEtElement(self, elem):

        """ Generate a xml.etree.ElementTree.Element from members.

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

    def __init__(self, data=[], xmlName = "", defaultValue = None,
            containingElement = None, state = State.States.ORIGINAL):

        simpleElementList = list()
        for item in data:
            newSimpleElement = SimpleElement(item, xmlName, defaultValue,
                    containingElement, state)
            simpleElementList.append(newSimpleElement)

        list.__init__(self, simpleElementList)
        XMLName.__init__(self, xmlName)
        State.__init__(self, state)
        Hierarchy.__init__(self, containingElement)
        Identifiable.__init__(self)
        self.defaultListElement = defaultValue


    def append(self, item):

        """ Envelope item into SimpleElement before appending to self.

        Envelope every type that is not of instance SimpleElement into an object
        of simple element, with the default values of the class object itself
        (xmlname, containintObject). The state is automatically set to
        state.State.States.ADDED
        """

        newElem = item
        if not isinstance(newElem, SimpleElement):
            newElem = SimpleElement(item, self.xmlName, self.defaultListElement,
                    self.containingObject, self.States.ADDED)
        else:
            newElem.state = State.States.ADDED

        list.append(self, newElem)


    def __eq__(self, other):

        return (list.__eq__(self, other) and
                XMLName.__eq__(self, other))


class Attribute(XMLName, Hierarchy, State, Identifiable):

    """ Attribute is used to represent XML attributes.

    Apart from the value of the attribute, also its Hierarchy, State (was it
    recently added, modified, deleted and name are stored. As well as all other
    XML representing classes, it implements Identifiable so it can be found by
    id.
    """

    def __init__(self, value, xmlName, defaultValue, containingElement,
            state = State.States.ORIGINAL):
        XMLName.__init__(self, xmlName)
        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        Identifiable.__init__(self)
        self.value = value
        self.defaultValue = defaultValue


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
            xmlName: str = "Project",
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function of Project """

        Hierarchy.__init__(self, None) # Project is the topmost element
        State.__init__(self, state)
        XMLName.__init__(self, xmlName)
        XMLIdentifiable.__init__(self, uuid)
        Identifiable.__init__(self)
        self._name = SimpleElement(name, "Name", "", self)
        self._extSchemaSrc = SimpleElement(extSchemaSrc, "ExtensionSchema",
                None, self)
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


    def deleteObject(self, object):

        """ Remove `object` from the data model (i.e. instance of Project)

        Removal is done depending on whether object is part of a list, if its a
        SimpleElement or Attribute or a complex element (e.g. instance of
        comment). From a list it will be removed, SimpleElements and Attributes
        are assigned their default value and complex objects are set to None.
        """

        debug("My id is {}".format(id(self)))
        parent = object.containingObject

        memberName = ""
        isList = False

        # find out the name of the member variable that references `object`
        # if `object` is part of a list then its name will be referenced by
        # `memberName`
        for (mName, mValue) in vars(parent).items():
            if issubclass(type(mValue), list):
                if object in mValue:
                    memberName = mName
                    isList = True
                    break
            # catch members that don't inherit Identifiable and thus aren't
            # applicable to deletion (e.g.: state, xmlName)
            elif not issubclass(type(mValue), Identifiable):
                continue
            elif object.id == mValue.id:
                memberName = mName
                break

        if memberName == "":
            msg = ("The name referencing {} in its parent {} could"\
                    " not be found").format(object, parent)
            debug(msg)
            util.printErr(msg)
            return False

        # remove the object fom the list
        if isList:
            l = getattr(parent, memberName)
            debug("Object to delete has id {}".format(id(object)))
            objIdx = l.index(object)
            l.remove(object)

        # set the object back to its default state
        else:
            debug("Removing {} from {}".format(memberName, object))
            objType = type(object)
            if (issubclass(objType, Attribute) or
                    issubclass(objType, SimpleElement)):
                object.value = object.defaultValue
                object.state = State.States.ORIGINAL
            else:
                setattr(parent, memberName, None)

        return self


    def getEtElement(self, elem):

        elem.tag = self.xmlName
        elem.attrib["ProjectId"] = str(self.xmlId)

        dflValue = self._name.defaultValue
        if self.name != dflValue:
            nameElem = ET.SubElement(elem, self._name.xmlName)
            nameElem = self._name.getEtElement(nameElem)

        return elem
