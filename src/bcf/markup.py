import bcf.reader as reader
from uuid import UUID
from datetime import datetime, date
from typing import List # used for custom type annotations
from bcf.uri import Uri
from bcf.modification import Modification
from bcf.topic import Topic, SnippetType

class Header:
    def __init__(self,
                ifcProjectId: UUID = None,
                ifcSpacialStructureElement: UUID = None,
                external: bool = True,
                filename: str = "",
                time: datetime = None,
                reference: Uri = None):

        """ Initialization function for Header """

        self.ifcProjectId = ifcProjectId
        self.ifcSpacialStructureElement = ifcSpacialStructureElement
        self.external = external
        self.filename = filename
        self.time = time
        self.reference = reference


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return (self.ifcProjectId == other.ifcProjectId and
                self.ifcSpacialStructureElement ==
                other.ifcSpacialStructureElement and
                self.external == other.external and
                self.filename == other.filename and
                self.time == other.time and
                self.reference == other.reference)


class ViewpointReference:

    """ Base class for Viewpoint. """

    def __init__(self,
            id: UUID,
            file: Uri = None,
            snapshot: Uri = None,
            index: int = 0):

        """ Initialisation function of ViewpointReference """

        self.id = id
        self.file = file
        self.snapshot = snapshot
        self.index = index
        self._viewpoint = None

    @property
    def viewpoint(self):
        return self._viewpoint


    @viewpoint.setter
    def viewpoint(self, newVal):
        self._viewpoint = newVal


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if other is None:
            return False

        if reader.DEBUG:
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


class Comment:

    """ Class holding all data about a comment """

    def __init__(self,
            creation: Modification,
            comment: str,
            viewpoint: ViewpointReference = None,
            lastModification: Modification = None):

        """ Initialisation function of Comment """

        self.creation = creation
        self.comment = comment
        self.viewpoint = viewpoint
        self.lastModification = lastModification


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        if other is None:
            return False

        if reader.DEBUG:
            if self.creation != other.creation:
                print("Creation is different")
            if self.comment != other.comment:
                print("Comment is different")
            if self.viewpoint != other.viewpoint:
                print("Viewpoint is different")
            if self.lastModification != other.lastModification:
                print("LastModification is different")

        return (self.creation == other.creation and
                self.comment == other.comment and
                self.viewpoint == other.viewpoint and
                self.lastModification == other.lastModification)


    def __str__(self):

        ret_str = ("Comment(\n\tcreation='{}', \n\tcomment='{}', \n\tviewpoint='{}',"\
                "\n\tlastModification='{}')").format(self.creation, self.comment,
                str(self.viewpoint), self.lastModification)
        return ret_str


class Markup:

    """ Every topic folder has exactly one markup.bcf file. This forms the
    starting point for the ui to get the data """

    def __init__(self,
            header: Header = None,
            topic: List[Topic] = list(),
            comments: List[Comment] = list(),
            viewpoints: List[ViewpointReference] = list()):

        """ Initialization function for Markup """

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
