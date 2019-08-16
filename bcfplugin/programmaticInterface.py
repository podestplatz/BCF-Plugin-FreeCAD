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

"""
Author: Patrick Podest
Date: 2019-08-16
Github: @podestplatz

**** Description ****
The programmaticInterface is like the brain of the whole plugin. It is were
everything from the frontend comes together and gets distributed to the
backend.
It fulfills two purposes:
    - providing an interface for controlling the plugin over the CLI
    - providing a library for the GUI part of the plugin, to access the data
      model.

Every function in here operates on `curProject`, which is the active instance
of the data model. No object of the data model is passes to the frontend,
rather for every retrieve operation a deepcopy of the result is created. This
ensures that the programmaticInterface remains in full control of the data
model at every point in time.
"""

import os
import re
import sys
import copy
import pytz
import shutil
import inspect
import logging
import datetime
from enum import Enum
from typing import List, Tuple
from uuid import uuid4, UUID

import bcfplugin
import bcfplugin.util as util
import bcfplugin.rdwr.reader as reader
import bcfplugin.rdwr.writer as writer
import bcfplugin.rdwr.project as p
import bcfplugin.rdwr.markup as m
from bcfplugin.rdwr.modification import (ModificationDate, ModificationAuthor,
        ModificationType)
from bcfplugin.rdwr.viewpoint import Viewpoint, OrthogonalCamera, PerspectiveCamera
from bcfplugin.rdwr.topic import Topic, DocumentReference, BimSnippet
from bcfplugin.rdwr.markup import Comment, Header, HeaderFile, ViewpointReference, Markup
from bcfplugin.rdwr.uri import Uri
from bcfplugin.rdwr.interfaces.identifiable import Identifiable
from bcfplugin.rdwr.interfaces.hierarchy import Hierarchy
from bcfplugin.rdwr.interfaces.state import State
from bcfplugin.rdwr.interfaces.xmlname import XMLName
from bcfplugin.frontend.viewController import CamType
from bcfplugin import FREECAD, GUI

__all__ = [ "CamType", "OperationResults", "deleteObject", "openProject", "closeProject",
        "getTopics", "getComments", "getViewpoints", "openIfcFile",
        "getRelevantIfcFiles", "getAdditionalDocumentReferences",
        "activateViewpoint", "addCurrentViewpoint",
        "addComment", "addFile", "addLabel", "addDocumentReference", "addTopic",
        "copyFileToProject", "modifyComment", "modifyElement", "saveProject",
        "getTopicFromUUID"
        ]

utc = pytz.UTC
""" For localized times """

curProject = None
""" This variable holds the reference to the currently active data model. """

App = None
""" Alias for the FreeCAD module """

Gui = None
""" Alias for the FreeCADGui module """

logger = bcfplugin.createLogger(__name__)

if GUI:
    import frontend.viewController as vCtrl
    import FreeCADGui as Gui

if FREECAD:
    import FreeCAD as App


class OperationResults(Enum):

    """ This enum is used by the programmaticInterface to report whether an
    operation has succeeded or failed. It is intended to be imported also by
    every module using the programmaticInterface. """

    SUCCESS = 1
    FAILURE = 2


def _handleProjectUpdate(errMsg, backup):

    """ Request for all updates to be written, and handle the results.

    If the update went through successful then the backup is deleted. Otherwise
    the current state is rolled back.
    """

    global curProject

    errorenousUpdate = writer.processProjectUpdates()
    if errorenousUpdate is not None:
        logger.error(errMsg)
        logger.info("Project state is reset to before the update.")
        oldProject = curProject
        curProject = backup
        del oldProject
        return OperationResults.FAILURE

    del backup
    return OperationResults.SUCCESS


def _getCallerFileName():

    """ Return the file name of the second to last function on the stack.

    This function assumes that it is called from another function inside this
    module.
    For every method a new stack frame is pushed onto the stack, thus the
    previous stack frame (gotten via `inspect.stack()[1]`) will be of the
    function inside this module. `_getCallerFileName` now returns the file name
    of the function that called the former.

    For example:
        a() -> b() -> _getCallerFileName()
        Returns module(a).__file__
    """

    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0])

    return module.__file__


def isProjectOpen():

    """ Check whether a project is currently open and display an error message

    Returns true if a project is currently open. False otherwise.
    """

    if curProject is None:
        return False
    return True


def saveProject(dstFile):

    """ Save the current state of the working directory to `dstfile` """

    logger.info("Saving the project to {}".format(dstFile))
    bcfRootPath = util.getBcfDir()
    writer.zipToBcfFile(bcfRootPath, dstFile)


def openProject(bcfFile):

    """ Reads in the given bcfFile and makes it available to the plugin.

    bcfFile is read using reader.readBcfFile(), if it returned `None` it is
    assumed that the file is invalid and the user is notified.
    """

    global curProject

    logger.info("Opening {}".format(bcfFile))
    if not os.path.exists(bcfFile):
        logger.error("File {} does not exist. Please choose a valid"\
            " file!".format(bcfFile))
        return OperationResults.FAILURE

    project = reader.readBcfFile(bcfFile)
    if project is None:
        logger.error("{} could not be read.".format(bcfFile))
        return OperationResults.FAILURE

    curProject = project
    return OperationResults.SUCCESS


def closeProject():

    """ Encompasses an interactive CLI close project prompt.

    First the user is given the choice to save the dirty state or discard it.
    If he/she wants to save the state the path to the file (the state shall be
    stored to) is requested. With this path the `saveProject` is then called.
    After a successful operation, the data model is deleted.
    """

    global curProject

    logger.info("Closing project...")
    if util.getDirtyBit():

        answer = "x"
        while answer not in "ny " and answer != "":
            answer = input("Do you want to save your changes before exiting?"\
                    "([y]|n)")

        if answer == "y" or answer == " " or answer == "":
            currentDir = os.path.dirname(os.path.abspath(__file__))
            print("Current directory: {}".format(currentDir))
            file = input("File to save to: ")
            if os.path.isabs(file):
                saveProject(file)
            else:
                saveProject(os.path.join(currentDir, file))

    del curProject
    util.deleteTmp()


def _searchRealTopic(topic: Topic):

    """ Searches `curProject` for `topic` and returns the result

    If not found then an error message is printed in addition
    """

    global curProject

    logger.debug("Retrieving original copy of topic: {}".format(topic.title))
    realTopic = curProject.searchObject(topic)
    if realTopic is None:
        logger.error("Topic {} could not be found in the open project."\
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


def openIfcFile(path: str):

    """ Opens an IfcFile behind path. IfcOpenShell is required! """

    logger.info("Opening IFC file {} in FreeCAD".format(path))
    if not os.path.exists(path):
        logger.error("File {} could not be found. Please supply a path that"\
                "exists")
        return OperationResults.FAILURE

    if not FREECAD:
        logger.error("I am not running inside FreeCAD. {} can only be opened"\
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


def activateViewpoint(viewpoint: Viewpoint,
        camType: CamType = CamType.PERSPECTIVE):

    """ Sets the camera view the model from the specified viewpoint."""

    logger.info("Activating viewpoint")
    if not (GUI and FREECAD):
        logger.error("Application is running either not inside FreeCAD or without"\
                " Gui. Thus cannot set camera position")
        return OperationResults.FAILURE

    if (Gui.ActiveDocument is None or
            Gui.ActiveDocument.ActiveView is None):
        logger.error("There is no document or view active. Thus cannot apply"\
                " any viewpoint settings.")
        return OperationResults.FAILURE

    # Apply camera settings
    camSettings = None
    if camType == CamType.ORTHOGONAL:
        camSettings = viewpoint.oCamera
    elif camType == CamType.PERSPECTIVE:
        camSettings = viewpoint.pCamera
    else:
        logger.error("Camera type {} does not exist.".format(camType))
        return OperationResults.FAILURE

    if camSettings is None:
        logger.error("No camera settings found in viewpoint"\
                " {}".format(viewpoint))
        return OperationResults.FAILURE

    if camType == CamType.ORTHOGONAL:
        vCtrl.setOCamera(camSettings)
    elif camType == CamType.PERSPECTIVE:
        vCtrl.setPCamera(camSettings)

    # Apply visibility component settings
    # Thereby the visibility of each specified component, the colour and its
    # selection is set.
    # NOTE: ViewSetupHints are not applied atm
    if viewpoint.components is not None:
        components = viewpoint.components
        vCtrl.applyVisibilitySettings(components.visibilityDefault,
                components.visibilityExceptions)
        vCtrl.colourComponents(components.colouring)
        vCtrl.selectComponents(components.selection)

    # check if any clipping planes are defined and create everyone if so.
    if (viewpoint.clippingPlanes is not None and
            len(viewpoint.clippingPlanes) > 0):
        for clip in viewpoint.clippingPlanes:
            vCtrl.createClippingPlane(clip)


def resetView():

    """ Reset FreeCAD's view to the state it was prior to activating the
    first viewpoint """

    logger.info("Resetting view to original state")
    if not (GUI and FREECAD):
        logger.error("Application is running either not inside FreeCAD or without"\
                " GUI. Thus cannot set camera position")
        return OperationResults.FAILURE

    vCtrl.resetView()


def _isIfcGuid(guid: str):

    """ Check whether `guid` is an ifc guid.

    According to `markup.xsd` of version 2.1 an ifcguid is composed of 22 alpha
    numeric characters + '_' and '$'.
    Regex: [0-9,A-Z,a-z,_$]
    """

    if len(guid) != 22:
        return False

    pattern = re.compile("[0-9,A-Z,a-z,_$]*")
    if pattern.fullmatch(guid) is None:
        return False
    return True


def copyFileToProject(path: str, destName: str = "", topic: Topic = None):

    """ Copy the file behind `path` into the working directory.

    If `topic` is not None and references an existing topic in the project then
    the file behind path is copied into the topic directory. Otherwise it is
    copied into the root directory of the project.
    If `destName` is given the resulting filename will be the value of
    `destName`. Otherwise the original filename is used.
    Before everything takes place, a backup of the current project is made. If
    an error occurs, the current project will be rolled back to the backup.
    """

    global curProject

    logger.info("Copying file {} into the project".format(path))
    if not os.path.exists(path):
        logger.error("File `{}` does not exist. Nothing is beeing copied.")
        return OperationResults.FAILURE

    if not isProjectOpen():
        return OperationResults.FAILURE

    srcFileName = os.path.basename(path)
    dstFileName = srcFileName if destName == "" else destName
    destPath = util.getBcfDir()
    if topic is not None:
        realTopic = _searchRealTopic(topic)
        if realTopic is None:
            return OperationResults.FAILURE

        destPath = os.path.join(destPath, str(realTopic.xmlId))
    destPath = os.path.join(destPath, dstFileName)

    i = 1
    while os.path.exists(destPath):
        if i == 1:
            logger.info("{} already exists.".format(destPath))

        dir, file = os.path.split(destPath)
        splitFN = dstFileName.split(".")
        splitFN[0] += "({})".format(i)
        file = ".".join(splitFN)
        destPath = os.path.join(dir, file)
        i += 1

    if i != 1:
        logger.info("Changed filename to {}.".format(destPath))

    shutil.copyfile(path, destPath)


def setModDateAuthor(element, author="", addUpdate=True):

    """ Update the modAuthor and modDate members of element """

    logger.debug("Updating ModifiedDate and ModifiedAuthor in"\
            " {}".format(element))
    # timestamp used as modification datetime
    modDate = utc.localize(datetime.datetime.now())

    oldDate = element.modDate
    element.modDate = modDate

    # set the modAuthor if `author` is set
    if author != "" and author is not None:
        oldAuthor = element.modAuthor
        element.modAuthor = author
    # if author is left empty, the previous modification author will be
    # overwritten
    elif author == "" or author is None:
        # print info if the author is not set
        logger.info("Author is not set.")
        element.modAuthor = element._modAuthor.defaultValue

    # add the author/date modification as update to the writers module
    if addUpdate:
        element._modDate.state = State.States.MODIFIED
        writer.addProjectUpdate(curProject, element._modDate, oldDate)

        if author != "" and author is not None:
            element._modAuthor.state = State.States.MODIFIED
            writer.addProjectUpdate(curProject, element._modAuthor, oldDate)


def getProjectName():

    """ Return the name of the open project """

    return curProject.name


def getTopics():

    """ Retrieves ordered list of topics from the currently open project.

    A list is constructed that holds tuples, in which the first element contains
    the name of the topic and the second element is a copy of the topic object
    itself.
    The list is sorted based on the index a topic is assigned to. Topics without
    an index are shown as last elements.
    """

    logger.debug("Retrieving list of topics in the project")
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

    global curProject

    logger.debug("Retrieving comments to topic {}".format(topic.title))
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


def getViewpoints(topic: Topic, realViewpoint = True):

    """ Collect a list of viewpoints associated with the given topic.

    The list is constructed of tuples. Each tuple element contains the name of
    the viewpoint file and a reference to the read-in viewpoint.
    If the list cannot be constructed, because for example no project is
    currently open, OperationResults.FAILURE is returned.
    If `realViewpoint` == True then the second element of every tuple is the
    viewpoint object itself referenced by the viewpoint reference. Otherwise it
    is the viewpoint reference.
    """

    global curProject

    logger.debug("Retrieving viewpoints to topic {}".format(topic.title))
    if not isProjectOpen():
        return OperationResults.FAILURE

    # given topic is a copy of the topic contained in curProject
    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    markup = realTopic.containingObject
    viewpoints = []
    if realViewpoint:
        viewpoints = [ (str(vpRef.file), copy.deepcopy(vpRef.viewpoint))
                for vpRef in markup.viewpoints ]
    else:
        viewpoints = [ (str(vpRef.file), copy.deepcopy(vpRef))
                for vpRef in markup.viewpoints ]


    return viewpoints


def getSnapshots(topic: Topic):

    """ Returns a list of files representing the snapshots contained in `topic`.

    No deep copy has to made here, since the list returnde by
    `markup.getSnapshotFileList()` is already a list of strings with no tie to
    the data model.
    Every entry of the list returned by `markup.getSnapshotFileList()` is
    assumed to be just the filename of the snapshot file. Thus the string is
    joined with the path to the working directory.
    """

    logger.debug("Retrieving snapshots for topic {}".format(topic.title))
    if not isProjectOpen():
        return OperationResults.FAILURE

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    markup = realTopic.containingObject
    snapshots = markup.getSnapshotFileList()

    topicDir = os.path.join(util.getBcfDir(), str(realTopic.xmlId))
    return [ os.path.join(topicDir, snapshot) for snapshot in snapshots ]


def getRelevantIfcFiles(topic: Topic):

    """ Return a list of Ifc files relevant to this topic.

    This list is basically markup.Header.files. files is further filtered for
    ones that at least have the attribute IfcProjectId and a path associated.
    If the list cannot be constructed, because for example no project is
    currently open, OperationResults.FAILURE is returned.
    """

    global curProject

    logger.debug("Retrieving list of relevant IFC files for topic"\
            " {}".format(topic.title))
    if not isProjectOpen():
        return OperationResults.FAILURE

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    markup = realTopic.containingObject
    if markup.header is None:
        return []

    files = copy.deepcopy(markup.header.files)

    hasIfcProjectId = lambda file: file.ifcProjectId != file._ifcProjectId.defaultValue
    hasReference = lambda file: file.reference != file._reference.defaultValue
    files = filter(lambda f: hasIfcProjectId(f) and hasReference(f), files)

    logger.info("If you want to open one of the files in FreeCAD run:\n"\
            "\t plugin.openIfcProject(file)")

    return list(files)


def getAdditionalDocumentReferences(topic: Topic):

    """ Returns a list of all document references of a topic """

    global curProject

    logger.debug("Retrieving list of document references to topic"\
            " {}".format(topic.title))
    if not isProjectOpen():
        return OperationResults.FAILURE

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        return OperationResults.FAILURE

    docRefs = [ (ref.description, copy.deepcopy(ref))
                for ref in realTopic.docRefs ]
    return docRefs


def getTopic(element):

    """ Returns the topic to which `element` is associated.

    If `element` could not be found inside the current project `None` is
    returned. If `element` could not be associated to any existing topic `None`
    is returned. In the case that this function is called from outside this
    module (`programmaticInterface.py`), a deep copy of the found topic is
    returned.
    """

    logger.debug("Retrieving topic associated to {}".format(element))
    realElement = curProject.searchObject(element)
    if realElement is None:
        logger.erroror("Element {} could not be found in the current project.")
        return None

    elemHierarchy = realElement.getHierarchyList()

    topic = None
    for elem in elemHierarchy:
        if isinstance(elem, Markup):
            topic = elem.topic
            break
        elif isinstance(elem, Topic):
            topic = elem
            break
        else:
            continue

    if _getCallerFileName() == __file__:
        return topic
    elif topic is not None:
        topicCpy = copy.deepcopy(topic)
        return topicCpy
    else:
        return None


def getTopicFromUUID(uid: UUID):

    """ Search the data model for a topic where `topic.xmlId == uid` holds. """

    global curProject

    logger.debug("Searching data model for topic with UUID {}".format(uid))
    if not isProjectOpen():
        logger.error("The project is not open. Open a project before"\
                " trying to retrieve a topic by UUID.")
        return OperationResults.FAILURE

    if not isinstance(uid, UUID):
        logger.error("uid is not of type UUID. Can only get topic by UUID.")
        return OperationResults.FAILURE

    match = None
    topics = [ item.topic for item in curProject.topicList ]
    for topic in topics:
        if topic.xmlId == uid:
            match = copy.deepcopy(topic)
            break

    if match is None:
        logger.error("Could not find a topic to that uid: {}".format(str(uid)))
        return OperationResults.FAILURE

    return match


def addProject(name: str, extensionSchemaUri: ""):

    """ Adds a new project to the current working directory.

    This means essentially creating a new folder named `name` and placing one
    new file in it, namely `project.bcfp`."""

    global curProject

    logger.info("Adding new project with name {}".format(name))
    newProject = p.Project(uuid4(), name, extensionSchemaUri)
    newProject.state = State.States.ADDED

    writer.addProjectUpdate(newProject, newProject, None)
    result = _handleProjectUpdate("Project could not be created", None)
    if result == OperationResults.SUCCESS:
        curProject = copy.deepcopy(newProject)

    return result


def addViewpointToComment(comment: Comment, viewpoint: ViewpointReference, author: str):

    """ Add a reference to `viewpoint` inside `comment`.

    If `comment` already referenced a viewpoint then it is updated. If no
    viewpoint was refrerenced before then a new xml node is created. In both
    cases `ModifiedAuthor` (`modAuthor`) and `ModifiedDate` (`modDate`) are
    updated/set.
    Before everything takes place, a backup of the current project is made. If
    an error occurs, the current project will be rolled back to the backup.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Adding new viewpoint reference to comment {}".format(comment))

    if author == "":
        logger.info("`author` is empty. Cannot update without an author.")
        return OperationResults.FAILURE

    if not isProjectOpen():
        return OperationResults.FAILURE

    realComment = curProject.searchObject(comment)
    realViewpoint = curProject.searchObject(viewpoint)
    if realComment == None:
        logger.error("No matching comment was found in the current project.")
        return OperationResults.FAILURE

    if realViewpoint == None:
        logger.error("No matching viewpoint was found in the current project.")
        return OperationResults.FAILURE

    modDate = utc.localize(datetime.datetime.now())

    realComment.state = State.States.DELETED
    writer.addProjectUpdate(curProject, realComment, None)

    realComment.viewpoint = viewpoint
    realComment.state = State.States.ADDED
    writer.addProjectUpdate(curProject, realComment, None)

    oldDate = realComment.modDate
    realComment.modDate = modDate
    realComment._modDate.state = State.States.MODIFIED
    writer.addProjectUpdate(curProject, realComment._modDate, oldDate)

    oldAuthor = realComment.modAuthor
    realComment.modAuthor = author
    realComment._modAuthor.state = State.States.MODIFIED
    writer.addProjectUpdate(curProject, realComment._modAuthor, oldAuthor)

    return _handleProjectUpdate("Could not assign viewpoint.", projectBackup)


def addCurrentViewpoint(topic: Topic):

    """ Reads the current view settings and adds them as viewpoint to `topic`

    The view settings include:
        - selection state of each ifc object
        - color of each ifc object
        - camera position and orientation
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Adding current view settings as viewpoint to topic"\
            " {}".format(topic.title))

    if not (GUI and FREECAD):
        logger.error("Application is running either not inside FreeCAD or without"\
                " GUI. Thus cannot set camera position")
        return OperationResults.FAILURE

    doNotAdd = False
    if not isProjectOpen():
        logger.info("Project is not open. Viewpoint cannot be added to any"\
                " topic")
        doNotAdd = True

    realTopic = _searchRealTopic(topic)
    if realTopic is None:
        logger.info("Viewpoint will not be added.")
        doNotAdd = True

    camSettings = None
    try:
        camSettings = vCtrl.readCamera()
    except AttributeError as err:
        logger.error("Camera settings could not be read. Make sure the 3D"\
                " view is active.")
        logger.error(str(err))
        return OperationResults.FAILURE
    else:
        if camSettings is None:
            return OperationResults.FAILURE

    if not doNotAdd:
        realMarkup = realTopic.containingObject
        vpGuid = uuid4()
        oCamera = None
        pCamera = None
        if isinstance(camSettings, OrthogonalCamera):
            oCamera = camSettings
        elif isinstance(camSettings, PerspectiveCamera):
            pCamera = camSettings

        logger.info(str(camSettings))
        vp = Viewpoint(vpGuid, None, oCamera, pCamera)
        vp.state = State.States.ADDED
        vpFileName = writer.generateViewpointFileName(realMarkup)
        vpRef = ViewpointReference(vpGuid, Uri(vpFileName), None, -1, realMarkup,
                State.States.ADDED)
        vpRef.viewpoint = vp
        realMarkup.viewpoints.append(vpRef)

        writer.addProjectUpdate(curProject, vpRef, None)
        return _handleProjectUpdate("Viewpoint could not be added. Rolling"\
                " back to previous state", projectBackup)

    print(camSettings)
    return OperationResults.SUCCESS


def addTopic(title: str, author: str, type: str = "", description = "",
        status: str = "", priority: str = "", index: int = -1,
        labels: List[str] = list(), dueDate: datetime = None, assignee: str = "",
        stage: str = "", relatedTopics: List[UUID] = list(),
        referenceLinks: List[str] = list(), bimSnippet: BimSnippet = None):

    """ Adds a new topic to the project.

    That entails that a new topic folder is created in the bcf file as well as
    a new markup file created, with nothing set but the topic.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Adding new topic({}) to project({})".format(title,
        curProject.name))

    if not isProjectOpen():
        return OperationResults.FAILURE

    # new guid for topic
    guid = uuid4()

    # create and add new markup to curProject, bot nto write yet
    newMarkup = Markup(None, state = State.States.ADDED,
            containingElement = curProject)
    curProject.topicList.append(newMarkup)

    # create new topic and assign it to newMarkup
    creationDate = utc.localize(datetime.datetime.now())
    newTopic = Topic(guid, title, creationDate, author, type, status,
            referenceLinks, list(), priority, index, labels, None, "",
            dueDate, assignee, description, stage, relatedTopics, bimSnippet,
            newMarkup)
    # state does not have to be set. Topic will be automatically added when
    # adding the markup

    newMarkup.topic = newTopic
    writer.addProjectUpdate(curProject, newMarkup, None)

    return _handleProjectUpdate("Could not add topic {} to"\
            " project.".format(title), projectBackup)


def addComment(topic: Topic, text: str, author: str,
        viewpoint: Viewpoint = None):

    """ Add a new comment with content `text` to the topic.

    The date of creation is sampled right at the start of this function.
    Before everything takes place, a backup of the current project is made. If
    an error occurs, the current project will be rolled back to the backup.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Adding comment {} to topic {}".format(text, topic.title))

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
        logger.error("Error while adding {}".format(errorenousUpdate[1]))
        logger.error("Project is reset to before the addition.")
        logger.info("Please fix comment {}".format(comment))
        curProject = projectBackup

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
    Before everything takes place, a backup of the current project is made. If
    an error occurs, the current project will be rolled back to the backup.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Adding new file({}) to topic({})".format(filename, topic.title))

    if not isExternal:
        if not util.doesFileExistInProject(reference):
            logger.error("{} does not exist inside the project. Please check"\
                    " the path. Or for copiing a new file to the project use: "\
                    " plugin.copyFile(topic, fileAbsPath)".format(reference))
            return OperationResults.FAILURE
    elif not os.path.exists(reference):
        logger.error("{} could not be found. Please check the path for"\
                " typos".format(reference))
        return OperationResults.FAILURE

    if not _isIfcGuid(ifcProject) or ifcProject == "":
        logger.error("{} is not a valid IfcGuid. An Ifc guid has to be of"\
                " length 22 and contain alphanumeric characters including '_'"\
                " and '$'".format(ifcProject))

    if (not _isIfcGuid(ifcSpatialStructureElement) or
            ifcSpatialStructureElement == ""):
        logger.error("{} is not a valid IfcGuid. An Ifc guid has to be of"\
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
            " last valid state", projectBackup)


def addDocumentReference(topic: Topic,
        guid: str = "",
        isExternal: bool = False,
        path: str = "",
        description: str = ""):

    """ Creates a new document reference and adds it to `topic`.

    guid is the guid of the documentreference. If left alone a new random guid
    is generated using uuid.uuid4().
    isExternal == True => `path` is expected to be an absolute url,
    isExternal == False => `path` is expected to be a relative url pointing to
    a file in the project directory.
    `path` to the file, and `description` is a human readable name of the
    document.
    Before everything takes place, a backup of the current project is made. If
    an error occurs, the current project will be rolled back to the backup.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Adding new document reference({}) to topic"\
            " {}".format(description, topic.title))

    if (path == "" and description == ""):
        logger.info("Not adding an empty document reference")
        return OperationResults.FAILURE

    if not isExternal:
        if not util.doesFileExistInProject(topic, path):
            logger.error("{} does not exist inside the project. Please check"\
                    " the path. Or for copiing a new file to the project use: "\
                    " plugin.copyFile(topic, fileAbsPath)".format(path))
            return OperationResults.FAILURE
    elif not os.path.exists(path):
        logger.info("{} could not be found on the file system. Assuming"\
                " that it resides somewhere on a network.".format(path))

    # check if `guid` is a valid UUID and create a UUID object
    guidU = UUID(int=0)
    if isinstance(guid, UUID):
        guidU = guid
    elif guid == "":
        # just generate a new guid
        guidU = uuid4()
    else:
        try:
            guidU = UUID(guid)
        except ValueError as err:
            logger.error("The supplied guid is malformed ({}).".format(guid))
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
            State.States.ADDED)
    realTopic.docRefs.append(docRef)

    writer.addProjectUpdate(curProject, docRef, None)
    return _handleProjectUpdate("Document reference could not be added."\
            " Returning to last valid state...", projectBackup)


def addLabel(topic: Topic, label: str):

    """ Add `label` as new label to `topic`

    Before everything takes place, a backup of the current project is made. If
    an error occurs, the current project will be rolled back to the backup.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Adding new label({}) to topic {}".format(label, topic.title))

    if label == "":
        logger.info("Not adding an empty label.")
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
            " to last valid state...".format(label), projectBackup)


def deleteObject(object):

    """ Deletes an arbitrary object from curProject.

    The heavy lifting is done by writer.processProjectUpdates() and
    project.deleteObject(). Former deletes the object from the file and latter
    one deletes the object from the data model.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Deleting object {} from project".format(object.__class__))

    if not issubclass(type(object), Identifiable):
        logger.error("Cannot delete {} since it doesn't inherit from"\
            " interfaces.Identifiable".format(object))
        return OperationResults.FAILURE

    if not issubclass(type(object), Hierarchy):
        logger.error("Cannot delete {} since it seems to be not part of" \
            " the data model. It has to inherit from"\
            " hierarchy.Hierarchy".format(object))
        return OperationResults.FAILURE

    if not isProjectOpen():
        return OperationResults.FAILURE

    realObject = curProject.searchObject(object)
    if realObject is None:
        # No rollback has to be done here, since the state of the project is not
        # changed anyways.
        logger.error("Object {} could not be found in project {}".format(
            object.__class__, curProject.__class__))
        return OperationResults.FAILURE

    realObject.state = State.States.DELETED
    writer.addProjectUpdate(curProject, realObject, None)
    result = _handleProjectUpdate("Object could not be deleted from "\
            "data model" , projectBackup)

    # `result == None` if the update could not be processed.
    if result ==  OperationResults.FAILURE:
        curProject = projectBackup
        errMsg = "Couldn't delete {} from the file.".format(object)
        logger.error(errMsg)
        return OperationResults.FAILURE

    # otherwise the updated project is returned
    else:
        curProject = curProject.deleteObject(realObject)
        return OperationResults.SUCCESS


def modifyComment(comment: Comment, newText: str, author: str):

    """ Change the text of `comment` to `newText` in the data model.

    Alongside with the text, the modAuthor and modDate fields get overwritten
    with `author` and the current datetime respectively.
    If `newText` was left empty then the comment is going to be deleted.
    Before everything takes place, a backup of the current project is made. If
    an error occurs, the current project will be rolled back to the backup.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Modifying comment({})".format(comment))

    if newText == "":
        logger.info("newText is empty. Deleting comment now.")
        deleteObject(comment)
        return OperationResults.SUCCESS

    if not isProjectOpen():
        return OperationResults.FAILURE

    realComment = curProject.searchObject(comment)
    if realComment is None:
        logger.error("Comment {} could not be found in the data model. Not"\
                "modifying anything".format(comment))
        return OperationResulsts.FAILURE

    oldVal = realComment.comment
    realComment.comment = newText
    realComment._comment.state = State.States.MODIFIED
    writer.addProjectUpdate(curProject, realComment._comment, oldVal)

    # update `modDate` and `modAuthor`
    setModDateAuthor(realComment, author)

    return _handleProjectUpdate("Could not modify comment.", projectBackup)


def modifyElement(element, author=""):

    """ Replace the old element in the data model with element.

    A reference to the old element in the data model is acquired via the `id`
    member of `element`. This old element is updated with the new values. The
    corresponding XML element is first deleted from file and then added again
    with the new values.

    If `element` is of type Topic or Comment then `author` must be set, and then
    `modAuthor` and `modDate` are updated.
    """

    global curProject
    projectBackup = copy.deepcopy(curProject)
    logger.info("Modifying element {} in the"\
            " project".format(element.__class__))

    # ---- Checks ---- #
    if not isProjectOpen():
        return OperationResults.FAILURE

    # is element of the right type
    if not (issubclass(type(element), Identifiable) and
            issubclass(type(element), State) and
            issubclass(type(element), XMLName)):
        logger.error("Element is not an object from the data model. Cannot"\
                " update it")
        return OperationResults.FAILURE

    # ---- Operation ---- #
    # get a reference to the real element in the data model
    realElement = curProject.searchObject(element)
    if realElement is None:
        logger.error("{} object, that shall be changed, could not be"\
                " found in the current project.".format(element.xmlName))
        return OperationResults.FAILURE

    # get the associated topic
    realTopic = getTopic(realElement)
    if realTopic is None:
        logger.error("{} currently it is only possible to modify values of"\
                " markup.bcf.")
        return OperationResults.FAILURE

    realElement.state = State.States.DELETED
    writer.addProjectUpdate(curProject, realElement, None)

    # copy the state of the given element to the real element
    for property, value in vars(element).items():
        if property == "containingObject":
            continue
        setattr(realElement, property, copy.deepcopy(value))

    # if topic/comment was modified update `modDate` and `modAuthor`
    if isinstance(realElement, Topic) or isinstance(realElement, Comment):
        setModDateAuthor(realElement, author, False)

    realElement.state = State.States.ADDED
    writer.addProjectUpdate(curProject, realElement, None)
    realElement.state = State.States.ORIGINAL
    return _handleProjectUpdate("Could not modify element {}".format(element.xmlName),
            projectBackup)
