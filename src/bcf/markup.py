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

        return (self.id == other.id and
                self.file == other.file and
                self.snapshot == other.snapshot and
                self.index == other.index)


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

        return (self.creation == other.creation and
                self.comment == other.comment and
                self.viewpoint == other.viewpoint and
                self.lastModification == other.lastModification)


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
