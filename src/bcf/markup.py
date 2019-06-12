import xml.etree.ElementTree as ET
from uuid import UUID
from datetime import datetime, date
from typing import List # used for custom type annotations
from bcf.uri import Uri
from bcf.modification import Modification
from bcf.topic import Topic
from bcf.project import (SimpleElement, Attribute, DEBUG)
from bcf.viewpoint import (Viewpoint)
from interfaces.state import State
from interfaces.hierarchy import Hierarchy
from interfaces.identifiable import Identifiable
from interfaces.xmlname import XMLName

DEBUG = True

class HeaderFile(Hierarchy, State, XMLName):

    def __init__(self,
            ifcProjectId: str = "",
            ifcSpatialStructureElement: str = "",
            isExternal: bool = True,
            filename: str = "",
            time: datetime = None,
            reference: str = "",
            state: State.States = State.States.ORIGINAL,
            containingElement = None):

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self, "File")
        self._ifcProjectId = Attribute(ifcProjectId, "IfcProject", self)
        self._ifcSpatialStructureElement = Attribute(
                ifcSpatialStructureElement, "IfcSpatialStructureElement", self)
        self._external = Attribute(isExternal, "isExternal", self)
        self._filename = SimpleElement(filename, "Filename", self)
        self._time = SimpleElement(time, "Date", self)
        self._reference = SimpleElement(reference, "Reference", self)


    @property
    def ifcProjectId(self):
        return self._ifcProjectId.value

    @ifcProjectId.setter
    def ifcProjectId(self, newVal):
        self._ifcProjectId.value = newVal

    @property
    def reference(self):
        return self._reference.value

    @reference.setter
    def reference(self, newVal):
        self._reference.value = newVal

    @property
    def ifcSpatialStructureElement(self):
        return self._ifcSpatialStructureElement.value

    @ifcSpatialStructureElement.setter
    def ifcSpatialStructureElement(self, newVal):
        self._ifcSpatialStructureElement.value = newVal

    @property
    def external(self):
        return self._external.value

    @external.setter
    def external(self, newVal):
        self._external.value = newVal

    @property
    def filename(self):
        return self._filename.value

    @filename.setter
    def filename(self, newVal):
        self._filename.value = newVal

    @property
    def time(self):
        return self._time.value

    @time.setter
    def time(self, newVal):
        self._time.value = newVal

    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.ifcProjectId == other.ifcProjectId and
                self.ifcSpatialStructureElement ==
                other.ifcSpatialStructureElement and
                self.external == other.external and
                self.filename == other.filename and
                self.time == other.time and
                self.reference == other.reference)


    def getEtElement(self, elem):

        elem.tag = "File"

        elem.attrib["isExternal"] = str(self.external).lower() # xml bool is lowercase
        if self.ifcSpatialStructureElement != "":
            elem.attrib["IfcSpatialStructureElement"] = self.ifcSpatialStructureElement
        if self.ifcProjectId != "":
            elem.attrib["IfcProject"] = self.ifcProjectId

        if self.filename != "":
            filenameElem = ET.SubElement(elem, "Filename")
            filenameElem.text = self.filename
        if self.time is not None:
            timeElem = ET.SubElement(elem, "Date")
            timeElem.text = self.time.isoformat("T", "seconds")
        if self.reference != "":
            refElem = ET.SubElement(elem, "Reference")
            refElem.text = str(self.reference)

        print("Hello this is me {}".format(ET.dump(elem)))
        return elem


    def getStateList(self):

        stateList = list()
        if not self.isOriginal():
            stateList.append((self.state, self))

        stateList += self._ifcProjectId.getStateList()
        stateList += self._ifcSpatialStructureElement.getStateList()
        stateList += self._external.getStateList()
        stateList += self._filename.getStateList()
        stateList += self._reference.getStateList()

        return stateList


    def __str__(self):
        ret_str = ("ContainingElement(\n"\
                "isExternal: {}\n"\
                "ifcSpatialStructureElement: {}\n"\
                "ifcProject: {}\n"\
                "filename: {}\n"\
                "time: {}\n"\
                "reference: {})").format(self.external,
                        self.ifcSpatialStructureElement,
                        self.ifcProjectId,
                        self.filename,
                        self.time,
                        self.reference)
        return ret_str


class Header(Hierarchy, State, XMLName):

    """
    """

    def __init__(self,
                files: List[HeaderFile] = list(),
                containingElement = None,
                state: State = State.States.ORIGINAL):

        """ Initialization function for Header """

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.files = files
        for f in files:
            f.containingObject = self


    def getStateList(self):

        stateList = list()
        if not self.isOriginal():
            stateList.append((self.state, self))

        for f in self.files:
            stateList += f.getStateList()

        return stateList


class ViewpointReference(Hierarchy, State, Identifiable, XMLName):

    """ Base class for Viewpoint. """

    def __init__(self,
            id: UUID,
            file: Uri = None,
            snapshot: Uri = None,
            index: int = -1,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function of ViewpointReference """

        Hierarchy.__init__(self, containingElement)
        Identifiable.__init__(self, id)
        State.__init__(self, state)
        XMLName.__init__(self, "Viewpoints")
        self._file = SimpleElement(file, "Viewpoint", self)
        self._snapshot = SimpleElement(snapshot, "Snapshot", self)
        self._index = SimpleElement(index, "Index", self)
        self._viewpoint = None

    @property
    def file(self):
        return self._file.value

    @file.setter
    def file(self, newVal):
        if isinstance(newVal, Uri):
            self._file.value = newVal
        elif isinstance(newVal, str):
            self._file.value = Uri(newVal)
        else:
            raise ValueError("File only supports the types 'str' and 'Uri'."\
                    " Erroneous type is: {}".format(type(newVal)))

    @property
    def snapshot(self):
        return self._snapshot.value

    @snapshot.setter
    def snapshot(self, newVal):
        self._snapshot.value = newVal

    @property
    def index(self):
        return self._index.value

    @index.setter
    def index(self, newVal):
        self._index.value = newVal

    @property
    def viewpoint(self):
        return self._viewpoint

    @viewpoint.setter
    def viewpoint(self, newVal):
        if isinstance(newVal, Viewpoint):
            self._viewpoint = newVal
        elif newVal is None:
            self._viewpoint = None
        else:
            raise ValueError("The new value has to be of type `Viewpoint`."\
                " Erroneous type: {}".format(type(newVal)))


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if other is None:
            return False

        if DEBUG:
            if self.id != other.id:
                print("Viewpoint: id is different {} {}".format(self.id, other.id))
            if self.file != other.file:
                print("Viewpoint: file is different {} {}".format(
                    self.file, other.file))
            if self.snapshot != other.snapshot:
                print("Viewpoint: snapshot is different {} {}".format(
                    self.snapshot, other.snapshot))
            if self.index != other.index:
                print("Viewpoint: index is different {} {}".format(
                    self.index, other.index))

        return (self.id == other.id and
                self.file == other.file and
                self.snapshot == other.snapshot and
                self.index == other.index and
                self.viewpoint == other.viewpoint)


    def __str__(self):
        ret_str = ("ViewpointReference(id='{}', file='{}', snapshot='{}',"\
                        " index='{}')").format(self.id, self.file, self.snapshot,
                        self.index)
        return ret_str


    def getEtElement(self, elem):

        elem.attrib["Guid"] = str(self.id)

        if self.file is not None:
            fileElem = ET.SubElement(elem, "Viewpoint")
            fileElem.text = str(self.file)

        if self.snapshot is not None:
            snapElem = ET.SubElement(elem, "Snapshot")
            snapElem.text = str(self.snapshot)

        if self.index != -1:
            indexElem = ET.SubElement(elem, "Index")
            indexElem.text = str(self.index)

        return elem


    def getStateList(self):

        stateList = list()
        if not self.isOriginal():
            stateList.append((self.state, self))

        stateList += self._file.getStateList()
        stateList += self._snapshot.getStateList()
        stateList += self._index.getStateList()

        if self.viewpoint is not None:
            stateList += self._viewpoint.getStateList()

        if DEBUG:
            print("{}.getStateList(): returning {}".format(
                self.__class__.__name__, stateList))

        return stateList


class Comment(Hierarchy, Identifiable, State, XMLName):

    """ Class holding all data about a comment """

    def __init__(self,
            guid: UUID,
            creation: Modification,
            comment: str,
            viewpoint: ViewpointReference = None,
            lastModification: Modification = None,
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialisation function of Comment """

        Hierarchy.__init__(self, containingElement)
        Identifiable.__init__(self, guid)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.creation = creation
        self._comment = SimpleElement(comment, "Comment", self)
        self.viewpoint = viewpoint
        self._lastModification = lastModification


    @property
    def comment(self):
        return self._comment.value

    @comment.setter
    def comment(self, newVal):
        self._comment.value = newVal

    @property
    def lastModification(self):
        return self._lastModification

    @lastModification.setter
    def lastModification(self, newVal):
        self._lastModification = newVal
        self._lastModification.containingObject = self


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if other is None:
            return False

        if DEBUG:
            if self.creation != other.creation:
                print("Creation is different")
            if self.comment != other.comment:
                print("Comment is different")
            if self.viewpoint != other.viewpoint:
                print("Viewpoint is different")
            if self.lastModification != other.lastModification:
                print("LastModification is different")

        return (self.id == other.id and
                self.creation == other.creation and
                self.comment == other.comment and
                self.viewpoint == other.viewpoint and
                self.lastModification == other.lastModification)


    def __str__(self):

        ret_str = ("Comment(\n\tcreation='{}', \n\tcomment='{}', \n\tviewpoint='{}',"\
                "\n\tlastModification='{}')").format(self.creation, self.comment,
                str(self.viewpoint), self.lastModification)
        return ret_str


    def getEtElement(self, elem):

        elem.tag = self.xmlName
        elem.attrib["Guid"] = str(self.id)

        dateElem = ET.SubElement(elem, "Date")
        dateElem.text = self.creation.date.isoformat("T", "seconds")

        authorElem = ET.SubElement(elem, "Author")
        authorElem.text = self.creation.author

        commentElem = ET.SubElement(elem, "Comment")
        commentElem.text = self.comment

        if self.viewpoint is not None:
            vpElem = ET.SubElement(elem, "Viewpoint")
            vpElem.attrib["Guid"] = str(self.viewpoint.id)

        if self.lastModification is not None:
            modDateElem = ET.SubElement(elem, "ModifiedDate")
            modDateElem.text = self.lastModification.date.isoformat("T", "seconds")

            modAuthorElem = ET.SubElement(elem, "ModifiedAuthor")
            modAuthorElem.text = self.lastModification.author

        return elem


    def getStateList(self):

        stateList = list()
        if not self.isOriginal():
            stateList.append((self.state, self))

        stateList += self.creation.getStateList()
        stateList += self._comment.getStateList()
        # viewpoint is already added to list by Markup
        stateList += self.lastModification.getStateList()

        if DEBUG:
            print("{}.getStateList(): returning {}".format(
                self.__class__.__name__, stateList))

        return stateList


class Markup(Hierarchy, State, XMLName):

    """ Every topic folder has exactly one markup.bcf file. This forms the
    starting point for the ui to get the data """

    def __init__(self,
            topic: Topic,
            header: Header = None,
            comments: List[Comment] = list(),
            viewpoints: List[ViewpointReference] = list(),
            containingElement = None,
            state: State.States = State.States.ORIGINAL):

        """ Initialization function for Markup """

        Hierarchy.__init__(self, containingElement)
        State.__init__(self, state)
        XMLName.__init__(self)
        self.header = header
        self.topic = topic
        self.comments = comments
        self.viewpoints = viewpoints


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.header == other.header and
                self.topic == other.topic and
                self.comments == other.comments and
                self.viewpoints == other.viewpoints)


    def getViewpointRefByGuid(self, guid: UUID):

        """
        Searches in the list of viewpoints for one whose id matches `guid` and
        returns the first one found if more than one were found (wich should not
        happen btw). If none were found or the viewpoints list is `None` then
        `None` is returned.
        """

        if self.viewpoints is None:
            return None

        resultList = list(filter(lambda item: item.id == guid, self.viewpoints))
        if len(resultList) >= 1:
            return resultList[0]
        return None


    def getViewpointFileList(self):

        """
        From `self.viewpoints` extracts the `file` attributes and collects them in
        a list. Only entries different from `None` are colleced. Every element
        of the list is a tuple. Of this tuple the first element denotes the
        filename and the second one is a reference to the
        `ViewpointsReference` object it is contained in
        """

        vpList = [ (vp.file, vp) for vp in self.viewpoints
                    if vp.file ]
        return vpList


    def getSnapshotFileList(self):

        """
        From self.snapshots extracts the `snapshot` attributes and collects them in
        a list. Only entries different from `None` are colleced.
        """

        snapshotList = [ vp.snapshot for vp in self.viewpoints
                            if vp.snapshot ]
        return snapshotList


    def getStateList(self):

        stateList = list()
        if not self.isOriginal():
            stateList.append((self.state, self))

        stateList += self.topic.getStateList()
        if self.header is not None:
            stateList += self.header.getStateList()

        for comment in self.comments:
            stateList += comment.getStateList()

        for viewpoint in self.viewpoints:
            stateList += viewpoint.getStateList()

        if DEBUG:
            print("{}.getStateList(): returning {}".format(
                self.__class__.__name__, stateList))

        return stateList

