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

import os
import logging
import datetime
import xml.etree.ElementTree as ET
from uuid import UUID
from copy import deepcopy

import bcfplugin
from bcfplugin.rdwr.uri import Uri
from bcfplugin.rdwr.interfaces.hierarchy import Hierarchy
from bcfplugin.rdwr.interfaces.state import State
from bcfplugin.rdwr.interfaces.xmlname import XMLName
from bcfplugin.rdwr.interfaces.identifiable import XMLIdentifiable, Identifiable

logger = bcfplugin.createLogger(__name__)


def listSetContainingElement(itemList, containingObject):

    """ Sets the `containingElement` member of every item of `itemList` to
    `containingObject`. """

    if len(itemList) == 0:
        return None

    ignoreList = list()
    for item in itemList:
        if not issubclass(type(item), Hierarchy):
            index = itemList.index(item)
            ignoreList.append(index)

    for item in itemList:
        if itemList.index(item) not in ignoreList:
            item.containingObject = containingObject


def searchListObject(object, elementList):

    """ Invokes the `searchObject` algorithm of every element in `elementList`
    to search for `object`. """

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

    Every simple element is assigned a default value.
    If `value` contains `defaultValue`, that indicates to the
    containing object, that this member does not have to be serialized into an
    XML node.
    """

    typeDict = { "int": int, "float": float, "str": str }

    def __init__(self, value, xmlName, defaultValue, containingElement,
            state = State.States.ORIGINAL):
        XMLName.__init__(self, xmlName)
        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        Identifiable.__init__(self)
        # set value to default if it is None
        self._value = value if value else defaultValue
        self.defaultValue = defaultValue


    def __deepcopy__(self, memo):

        cpyid = deepcopy(self.id)
        cpyvalue = deepcopy(self.value)
        cpydeflvalue = deepcopy(self.defaultValue)
        cpyxmlname = deepcopy(self.xmlName)
        cpystate = deepcopy(self.state)

        cpy = SimpleElement(cpyvalue, cpyxmlname, cpydeflvalue, None, cpystate)
        cpy.id = cpyid
        cpy.state = self.state

        return cpy


    def __eq__(self, other):

        if type(self) != type(other):
            return False

        # None != None is assumed
        if self is None or other is None:
            return False

        return (self.value == other.value and
                self.xmlName == other.xmlName)


    def __str__(self):

        """ Return a stirng of the form '<Name>: <Value>' """

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
        if isinstance(self.value, datetime.datetime):
            elem.text = self.value.isoformat()
        else:
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


    def __deepcopy__(self, memo):

        """ Create a deepcopy of the object without copying `containingObject`

        Create a new list with deep copied elements.
        """

        cpyid = deepcopy(self.id, memo)
        cpyxmlname = deepcopy(self.xmlName, memo)
        cpydflvalue = deepcopy(self.defaultListElement, memo)
        tmpList = list()
        for item in self:
            cpyitem = deepcopy(item, memo)
            tmpList.append(cpyitem)

        cpy = SimpleList([ i.value for i in tmpList ],
                xmlName = cpyxmlname,
                defaultValue = cpydflvalue)
        # set the ids of the copied list items. They get reset in the
        # constructor
        for (newitem, cpyitem) in zip(cpy, tmpList):
            newitem.id = cpyitem.id
        cpy.id = cpyid
        cpy.state = self.state

        return cpy


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
        """
        else:
            newElem.state = State.States.ADDED
        """

        list.append(self, newElem)


    def __eq__(self, other):

        return (list.__eq__(self, other) and
                XMLName.__eq__(self, other))


class Attribute(XMLName, Hierarchy, State, Identifiable):

    """ Class used to represent XML attributes.

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
        # use default value if `value is None`
        self.value = value if value else defaultValue
        self.defaultValue = defaultValue


    def __deepcopy__(self, memo):

        cpyid = deepcopy(self.id)
        cpyvalue = deepcopy(self.value)
        cpydeflvalue = deepcopy(self.defaultValue)
        cpyxmlname = deepcopy(self.xmlName)
        cpystate = deepcopy(self.state)

        cpy = Attribute(cpyvalue, cpyxmlname, cpydeflvalue, None, cpystate)
        cpy.id = cpyid
        cpy.state = self.state

        return cpy


    def __str__(self):

        retstr = "{}:'{}'".format(self.xmlName, self.value)
        return retstr


    def searchObject(self, object):

        if not issubclass(type(object), Identifiable):
            return None

        id = object.id
        if self.id == id:
            return self
        else:
            return None


class Project(Hierarchy, State, XMLName, XMLIdentifiable, Identifiable):

    """ Represents for one the XML type project.xsd:Project and for the other
    the complete BCF file.

    From it a path to every other, properly instantiated object of the data
    model can be found.

    Deepcopies of project are created in the usual fashion, copying everything.
    However a deepcopy of just an element somewhere down the path, only copies
    downwards, and not back upwards again; which would be the case in the
    default implementation, because
    nearly every object inherits from `Hierarchy` supplying the class with a
    reference to its containing object.
    For example consider this graph:
                /-> Title  /-> Header
        Project \-> Markup \-> Topic
                            \-> Comment

    A copy of the markup node will copy all objects right from it, but the copy
    won't follow the path to the left to project.
    This behavior is obtained in two steps:
        1. a custom implementation of __deepcopy__ in every class
        2. the infusion of a temporary member into every "to-be-copied" object.
           This member determines whether the containing object reference shall
           also be copied or not.
    """

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


    def __deepcopy__(self, memo):

        """ Creates a complete deepcopy of the whole project """

        cpyid = deepcopy(self.id, memo)
        cpyxmlid = deepcopy(self.xmlId, memo)
        cpyname = deepcopy(self._name, memo)
        cpyextschemasrc = deepcopy(self._extSchemaSrc, memo)
        cpytopics = deepcopy(self.topicList, memo)

        cpy = Project(cpyxmlid)
        cpy.id = cpyid
        cpy.state = self.state
        cpy._name = cpyname
        cpy._extSchemaSrc = cpyextschemasrc
        cpy.topicList = cpytopics
        listSetContainingElement(cpy.topicList, cpy)

        members = [ cpy._name, cpy._extSchemaSrc ]
        listSetContainingElement(members, cpy)

        return cpy


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

        """ Searches this object and its members for one that matches
        `object.id`.

        The search algorithm, effectively implemented, is a depth first search. """

        if not issubclass(type(object), Identifiable):
            logger.error("object {} is not a subclass of Identifiable".format(object))
            return None

        # check if itself is the wanted object
        id = object.id
        if self.id == id:
            return self

        # search all non-list members
        members = [self._name, self._extSchemaSrc]
        searchResult = searchListObject(object, members)
        if searchResult is not None:
            return searchResult

        # search the list members
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
                    " not be found").format(object.__class__, parent.__class__)
            logger.error(msg)
            return None

        # remove the object fom the list
        if isList:
            l = getattr(parent, memberName)
            objIdx = l.index(object)
            l.remove(object)

        # set the object back to its default state
        else:
            objType = type(object)
            if (issubclass(objType, Attribute) or
                    issubclass(objType, SimpleElement)):
                object.value = object.defaultValue
                object.state = State.States.ORIGINAL
            else:
                setattr(parent, memberName, None)

        return self


    def getEtElement(self, elem):

        elem.tag = "ProjectExtension"

        projectElem = ET.SubElement(elem, self.xmlName)
        projectElem.attrib["ProjectId"] = str(self.xmlId)

        dflValue = self._name.defaultValue
        if self.name != dflValue:
            nameElem = ET.SubElement(projectElem, self._name.xmlName)
            nameElem = self._name.getEtElement(nameElem)

        # required element left empty
        extSchemaElem = ET.SubElement(elem, "ExtensionSchema")

        return elem
