import os
import sys
import copy
from enum import Enum

if __name__ == "__main__":
    sys.path.insert(0, "/home/patrick/projects/freecad/plugin/src")
    print(sys.path)
import bcf.reader as reader
import bcf.writer as writer
import bcf.project as p
from interfaces.identifiable import Identifiable
from interfaces.hierarchy import Hierarchy
from interfaces.state import State


curProject = None


class OperationResults(Enum):
    SUCCESS = 1
    FAILURE = 2


def printErr(msg):

    """ Print msg to stderr """

    print(msg, file=sys.stderr)


def deleteObject(object):

    """ Deletes an arbitrary object from curProject.

    The heavy lifting is done by writer.processProjectUpdates() and
    project.deleteObject(). Former deletes the object from the file and latter
    one deletes the object from the data model.
    """

    if not issubclass(type(object), Identifiable):
        printErr("Cannot delete {} since it doesn't inherit from"\
            " interfaces.Identifiable".format(object))
        return OperationResults.FAILURE

    if not issubclass(type(object), Hierarchy):
        printErr("Cannot delete {} since it seems to be not part of" \
            " the data model. It has to inherit from"\
            " hierarchy.Hierarchy".format(object))
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
        printErr(errMsg)
        return OperationResults.FAILURE

    # otherwise the updated project is returned
    else:
        curProject.deleteObject(object)
        return OperationResults.SUCCESS


def openProject(bcfFile):

    """ Reads bcfFile and sets curProject.

    bcfFile is read using reader.readBcfFile(), if it returned `None` it is
    assumed that the file is invalid and the user is notified.
    """

    global curProject

    if not os.path.exists(bcfFile):
        printErr("File {} does not exist. Please choose a valid"\
            " file!".format(bcfFile))
        return None

    project = reader.readBcfFile(bcfFile)
    if project is None:
        printErr("{} could not be read.".format(bcfFile))
        return None

    curProject = project


def getTopics():

    """ Retrieves ordered list of topics from the currently open project.

    A list is constructed that holds tuples, in which the first element contains
    the name of the topic and the second element is a copy of the topic object
    itself.
    The list is sorted based on the index a topic is assigned to. Topics without
    an index are shown as last elements.
    """

    if curProject is None:
        printErr("No project is open. Please open a project before trying to"\
            " retrieve topics")
        return OperationResults.FAILURE

    topics = list()
    for markup in curProject.topicList:
        topicTitle = markup.topic.title
        topic = markup.topic
        topics.append((topicTitle, topic))

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
