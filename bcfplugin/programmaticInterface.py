import os
import re
import sys
import copy
import pytz
import datetime
from enum import Enum
from typing import List, Tuple
from uuid import uuid4, UUID

import util
import rdwr.reader as reader
import rdwr.writer as writer
import rdwr.project as p
import rdwr.markup as m
from rdwr.viewpoint import Viewpoint
from rdwr.topic import Topic, DocumentReference
from rdwr.markup import Comment, Header, HeaderFile
from rdwr.interfaces.identifiable import Identifiable
from rdwr.interfaces.hierarchy import Hierarchy
from rdwr.interfaces.state import State

if util.GUI:
    import frontend.viewpointController as vpCtrl

__all__ = [ "CamType", "deleteObject", "openProject",
        "getTopics", "getComments", "getViewpoints", "openIfcFile",
        "getRelevantIfcFiles", "getAdditionalDocumentReferences",
        "activateViewpoint",
        "addComment", "addFile", "addLabel", "addDocumentReference" ]

utc = pytz.UTC
""" For localized times """

curProject = None

App = None
""" Alias for the FreeCAD module """

Gui = None
""" Alias for the FreeCADGui module """


class OperationResults(Enum):
    SUCCESS = 1
    FAILURE = 2


class CamType(Enum):
    ORTHOGONAL = 1
    PERSPECTIVE = 2


def isProjectOpen():

    """ Check whether a project is currently open and display an error message

    Returns true if a project is currently open. False otherwise.
    """

    if curProject is None:
        util.printErr("No project is open. Please open a project before trying to"\
            " retrieve topics")
        return False
    return True


def deleteObject(object):

    """ Deletes an arbitrary object from curProject.

    The heavy lifting is done by writer.processProjectUpdates() and
    project.deleteObject(). Former deletes the object from the file and latter
    one deletes the object from the data model.
    """

    global curProject

    if not issubclass(type(object), Identifiable):
        util.printErr("Cannot delete {} since it doesn't inherit from"\
            " interfaces.Identifiable".format(object))
        return OperationResults.FAILURE

    if not issubclass(type(object), Hierarchy):
        util.printErr("Cannot delete {} since it seems to be not part of" \
            " the data model. It has to inherit from"\
            " hierarchy.Hierarchy".format(object))
        return OperationResults.FAILURE

    if not isProjectOpen():
        return OperationResults.FAILURE

    # find out the name of the object in its parent
    object.state = State.States.DELETED

    projectCpy = copy.deepcopy(curProject)
    newObject = projectCpy.searchObject(object)
    writer.addProjectUpdate(projectCpy, newObject, None)
    result = writer.processProjectUpdates()

    # `result == None` if the update could not be processed.
    # ==> `result == projectCpy` will be returned to stay on the errorenous
    # state and give the user the chance to fix the issue.
    if result is not None:
        curProject = result[0]
        errMsg = "Couldn't delete {} from the file.".format(result[1])
        util.printErr(errMsg)
        return OperationResults.FAILURE

    # otherwise the updated project is returned
    else:
        curProject.deleteObject(object)
        return OperationResults.SUCCESS


def openProject(bcfFile):

    """ Reads in the given bcfFile and makes it available to the plugin.

    bcfFile is read using reader.readBcfFile(), if it returned `None` it is
    assumed that the file is invalid and the user is notified.
    """

    global curProject

    if not os.path.exists(bcfFile):
        util.printErr("File {} does not exist. Please choose a valid"\
            " file!".format(bcfFile))
        return OperationResults.FAILURE

    project = reader.readBcfFile(bcfFile)
    if project is None:
        util.printErr("{} could not be read.".format(bcfFile))
        return OperationResults.FAILURE

    curProject = project
    return OperationResults.SUCCESS


def getTopics():

    """ Retrieves ordered list of topics from the currently open project.

    A list is constructed that holds tuples, in which the first element contains
    the name of the topic and the second element is a copy of the topic object
    itself.
    The list is sorted based on the index a topic is assigned to. Topics without
    an index are shown as last elements.
    """

    if not isProjectOpen():
        return OperationResults.FAILURE

    topics = list()
    for markup in curProject.topicList:
        topic = copy.deepcopy(markup.topic)
        topics.append((topic.title, topic))

    # move all topics without an index to the end of the list
    topics = sorted(topics, key=lambda topic: topic[1].index)
    for i in range(0, len(topics)):
        topic = topics[i][1]

        if topic.index != topic._index.defaultValue:
            # first element with a valid index. No invalid indices will follow
            break

        if topic.index == topic._index.defaultValue:
            topics.append(topics[i])
            del topics[i]

    return topics


def _searchRealTopic(topic: Topic):
    """ Searches `curProject` for `topic` and returns the result

    If not found then an error message is printed in addition
    """

    realTopic = curProject.searchObject(topic)
    if realTopic is None:
        util.printErr("Topic {} could not be found in the open project."\
                "Cannot retrieve any comments for it then".format(topic))
    return realTopic


def _filterCommentsForViewpoint(comments: List[Tuple[str, m.Comment]], viewpoint: Viewpoint):

    """ Filter comments referencing viewpoint """

    if viewpoint is None:
        return comments

    realVp = curProject.searchObject(viewpoint)
    realVpRef = realVp.containingObject

    f = lambda cm:\
        cm if (cm[1].viewpoint and cm[1].viewpoint.id == realVpRef.id) else None
    filtered = list(filter(f, comments))
    return filtered


def getComments(topic: Topic, viewpoint: Viewpoint = None):

    """ Collect an ordered list of comments inside of topic.

    The list of comments is sorted by the date they were created in ascending
    order => oldest entries will be first in the list.
    Every list element item will be a tuple where the first element is the
    comments string representation and the second is the comment object itself.

    If this cannot be done OperationsResult.FAILURE is returned instead.

    If viewpoint is set then the list of comments is filtered for ones
    referencing viewpoint.
    """

    if not isProjectOpen():
        return OperationResults.FAILURE

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    markup = realTopic.containingObject
    comments = [ (str(comment), copy.deepcopy(comment)) for comment in markup.comments ]

    comments = sorted(comments, key=lambda cm: cm[1].date)
    comments = _filterCommentsForViewpoint(comments, viewpoint)
    return comments


def getViewpoints(topic: Topic):

    """ Collect a list of viewpoints associated with the given topic.

    The list is constructed of tuples. Each tuple element contains the name of
    the viewpoint file and a reference to the read-in viewpoint.
    If the list cannot be constructed, because for example no project is
    currently open, OperationResults.FAILURE is returned.
    """

    global curProject

    if not isProjectOpen():
        return OperationResults.FAILURE

    # given topic is a copy of the topic contained in curProject
    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    markup = realTopic.containingObject
    viewpoints = [ (str(vpRef.file), copy.deepcopy(vpRef.viewpoint))
            for vpRef in markup.viewpoints ]

    return viewpoints


def openIfcFile(path: str):

    """ Opens an IfcFile behind path. IfcOpenShell is required! """

    if not os.path.exists(path):
        util.printErr("File {} could not be found. Please supply a path that"\
                "exists")
        return OperationResults.FAILURE

    if not util.FREECAD:
        util.printErr("I am not running inside FreeCAD. {} can only be opened"\
                "inside FreeCAD")
        return OperationResults.FAILURE

    import importIFC as ifc
    ifc.open(path.encode("utf-8"))
    docName = join(os.path.basename(path).split('.')[:-1], '')
    App.setActiveDocument(docName)
    App.ActiveDocument = App.getDocument(docName)
    Gui.ActiveDocument = Gui.getDocument(docName)
    Gui.sendMsgToActiveView("ViewFit")

    return OperationResults.SUCCESS


def getRelevantIfcFiles(topic: Topic):

    """ Return a list of Ifc files relevant to this topic.

    This list is basically markup.Header.files. files is further filtered for
    ones that at least have the attribute IfcProjectId and a path associated.
    If the list cannot be constructed, because for example no project is
    currently open, OperationResults.FAILURE is returned.
    """

    global curProject

    if not isProjectOpen():
        return OperationResults.FAILURE

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    markup = realTopic.containingObject
    if markup.header is None:
        return []

    files = copy.deepcopy(markup.header.files)
    util.debug("files are {}".format(files))

    hasIfcProjectId = lambda file: file.ifcProjectId != file._ifcProjectId.defaultValue
    hasReference = lambda file: file.reference != file._reference.defaultValue
    files = filter(lambda f: hasIfcProjectId(f) and hasReference(f), files)

    util.printInfo("If you want to open one of the files in FreeCAD run:\n"\
            "\t plugin.openIfcProject(file)")

    return list(files)


def getAdditionalDocumentReferences(topic: Topic):

    """ Returns a list of all document references of a topic """

    global curProject

    if not isProjectOpen():
        return OperationResults.FAILURE

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    docRefs = [ (ref.description, copy.deepcopy(ref))
                for ref in realTopic.docRefs ]
    return docRefs


def activateViewpoint(viewpoint: Viewpoint, camType: CamType):

    """ Sets the camera view the model from the specified viewpoint."""

    if not (util.GUI and util.FREECAD):
        util.printErr("Application is running either not inside FreeCAD or without"\
                " GUI. Thus cannot set camera position")
        return OperationResults.FAILURE

    camSettings = None
    if camType == CamType.ORTHOGONAL:
        camSettings = viewpoint.oCamera
    elif camType == CamType.PERSPECTIVE:
        camSettings = viewpoint.pCamera
    else:
        util.printErr("Camera type {} does not exist.".format(camType))
        return OperationResults.FAILURE

    if camSettings is None:
        print(dir(util))
        util.printErr("No camera settings found in viewpoint {}")
        return OperationResults.FAILURE

    vpCtrl.setCamera(camSettings.viewPoint, camSettings.direction,
            camSettings.upVector)


def addComment(topic: Topic, text: str, author: str,
        viewpoint: Viewpoint = None):

    """ Add a new comment with content `text` to the topic.

    The date of creation is sampled right at the start of this function.
    """

    global curProject

    if not isProjectOpen():
        return OperationResults.FAILURE

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    realMarkup = realTopic.containingObject

    creationDate = datetime.datetime.now()
    localisedDate = utc.localize(creationDate)
    guid = uuid4() # generate new random id
    state = State.States.ADDED
    comment = Comment(guid, localisedDate, author, text, viewpoint,
            containingElement = realMarkup, state=state)
    realMarkup.comments.append(comment)

    writer.addProjectUpdate(curProject, comment, None)
    errorenousUpdate = writer.processProjectUpdates()
    if errorenousUpdate is not None:
        util.printErr("State is reset to the first errorenous update state.")
        util.printInfo("Please fix comment {}".format(comment))
        curProject = errorenousUpdate[0]


def _isIfcGuid(guid: str):

    """ Check whether `guid` is an ifc guid.

    According to `markup.xsd` of version 2.1 an ifcguid is composed of 22 alpha
    numeric characters + '_' and '$'.
    Regex: [0-9,A-Z,a-z,_$]
    """

    if len(guid) != 22:
        return False

    util.debug("checking {} of type {}".format(guid, type(guid)))

    pattern = re.compile("[0-9,A-Z,a-z,_$]*")
    if pattern.fullmatch(guid) is None:
        return False
    return True


def _handleProjectUpdate(errMsg):

    """ Request for all updates to be written, and handle the results. """

    errorenousUpdate = writer.processProjectUpdates()
    if errorenousUpdate is not None:
        util.printErr(errMsg)
        curProject = errorenousUpdate[0]
        return OperationResults.FAILURE
    return OperationResults.SUCCESS


def addFile(topic: Topic, ifcProject: str = "",
        ifcSpatialStructureElement: str = "",
        isExternal: bool = False,
        filename: str = "",
        reference: str = ""):

    """ Add a new IFC file to the project.

    This function assumes that the file already exists and only creates a
    reference to it inside the data model. It does not copy an external file
    into the project.
    """

    global curProject

    if not isExternal:
        if not util.doesFileExistInProject(reference):
            util.printErr("{} does not exist inside the project. Please check"\
                    " the path. Or for copiing a new file to the project use: "\
                    " plugin.copyFile(topic, fileAbsPath)".format(reference))
            return OperationResults.FAILURE
    elif not os.path.exists(reference):
        util.printErr("{} could not be found. Please check the path for"\
                " typos".format(reference))
        return OperationResults.FAILURE

    if not _isIfcGuid(ifcProject) or ifcProject == "":
        util.printErr("{} is not a valid IfcGuid. An Ifc guid has to be of"\
                " length 22 and contain alphanumeric characters including '_'"\
                " and '$'".format(ifcProject))

    if (not _isIfcGuid(ifcSpatialStructureElement) or
            ifcSpatialStructureElement == ""):
        util.printErr("{} is not a valid IfcGuid. An Ifc guid has to be of"\
                " length 22 and contain alphanumeric characters including '_'"\
                " and '$'".format(ifcProject))

    if not isProjectOpen():
        return OperationResults.FAILURE

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    realMarkup = realTopic.containingObject

    # create new header file and insert it into the data model
    creationDate = datetime.datetime.now()
    localisedDate = utc.localize(creationDate)
    newFile = HeaderFile(ifcProject, ifcSpatialStructureElement, isExternal,
            filename, localisedDate, reference, state = State.States.ADDED)
    # create markup.header if needed
    if realMarkup.header is None:
        realMarkup.header = Header([newFile])
        realMarkup.header.state = State.States.ADDED
        realMarkup.header.containingObject = realMarkup
        writer.addProjectUpdate(curProject, realMarkup.header, None)
    else:
        realMarkup.header.files.append(newFile)
    newFile.containingObject = realMarkup.header

    writer.addProjectUpdate(curProject, newFile, None)
    return _handleProjectUpdate("File could not be added. Project is reset to"\
            " last valid state")


def addDocumentReference(topic: Topic,
        guid: str = "",
        isExternal: bool = False,
        path: str = "",
        description: str = ""):

    """ Creates a new document reference and adds it to `topic`.

    guid is the guid of the documentreference.
    isExternal == True => `path` is expected to be an absolute url,
    isExternal == False => `path` is expected to be a relative url pointing to
    a file in the project directory.
    `path` to the file, and `description` is a human readable name of the
    document.
    """

    global curProject

    if (path == "" and description == ""):
        util.printInfo("Not adding an empty document reference")
        return OperationResults.FAILURE

    if not isExternal:
        if not util.doesFileExistInProject(path):
            util.printErr("{} does not exist inside the project. Please check"\
                    " the path. Or for copiing a new file to the project use: "\
                    " plugin.copyFile(topic, fileAbsPath)".format(path))
            return OperationResults.FAILURE
    elif not os.path.exists(reference):
        util.printInfo("{} could not be found on the file system. Assuming"\
                " that it resides somewhere on a network.".format(path))

    # check if `guid` is a valid UUID and create a UUID object
    guidU = UUID(int=0)
    if isinstance(guid, UUID):
        guidU = guid
    else:
        try:
            guidU = UUID(guid)
        except ValueError as err:
            util.printErr("The supplied guid is malformed ({}).".format(guid))
            return OperationResults.FAILURE

    if not isProjectOpen():
        return OperationResults.FAILURE

    # get a reference of the tainted, supplied topic reference in the working
    # copy of the project
    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    docRef = DocumentReference(guidU,
            isExternal, path,
            description, realTopic,
            state.States.ADDED)
    realTopic.docRefs.append(docRef)

    writer.addProjectUpdate(curProject, docRef, None)
    return _handleProjectUpdate("Document reference could not be added."\
            " Returning to last valid state...")


def addLabel(topic: Topic, label: str):

    """ Add `label` as new label to `topic` """

    global curProject

    if label == "":
        util.printInfo("Not adding an empty label.")
        return OperationResults.FAILURE

    if not isProjectOpen():
        return OperationResults.FAILURE

    # get a reference of the tainted, supplied topic reference in the working
    # copy of the project
    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    # create and add a new label to curProject
    realTopic.labels.append(label)
    addedLabel = realTopic.labels[-1] # get reference to added label

    writer.addProjectUpdate(curProject, addedLabel, None)
    return _handleProjectUpdate("Label '{}' could not be added. Returning"\
            " to last valid state...".format(label))
