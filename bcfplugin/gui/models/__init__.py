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

__all__ = ["openProjectBtnHandler", "getProjectName", "saveProject",
        "addTopic", "createProject", "RelatedTopicsModel", "TopicListModel",
        "SnapshotModel", "CommentModel", "ViewpointsListModel",
        "TopicMetricsModel", "AdditionalDocumentsModel"]

from bcfplugin.gui.models.relatedtopicsmodel import RelatedTopicsModel
from bcfplugin.gui.models.topiclistmodel import TopicListModel
from bcfplugin.gui.models.snapshotmodel import SnapshotModel
from bcfplugin.gui.models.commentmodel import CommentModel
from bcfplugin.gui.models.viewpointsmodel import ViewpointsListModel
from bcfplugin.gui.models.topicmetricsmodel import TopicMetricsModel
from bcfplugin.gui.models.additionaldocumentsmodel import AdditionalDocumentsModel

from bcfplugin import programmaticInterface as pI


def openProjectBtnHandler(file):

    """ Handler of the "Open" button for a project """

    pI.openProject(file)


def getProjectName():

    """ Wrapper for programmaticInterface.getProjectName() """

    return pI.getProjectName()


def saveProject(dstFile):

    """ Wrapper for programmaticInterface.saveProject() """

    pI.saveProject(dstFile)


def addTopic(newTopic: dict):

    """ Adds a topic to the internal data model by using
    programmaticInterface's addTopic() function """

    result = pI.addTopic(newTopic["title"], newTopic["author"],
            newTopic["type"], newTopic["description"], newTopic["status"],
            newTopic["priority"], newTopic["index"], newTopic["labels"],
            newTopic["dueDate"], newTopic["assignee"], newTopic["stage"])

    if result == pI.OperationResults.FAILURE:
        return False
    return True


def createProject(name: str, extSchema: str):

    """ Creates a new project by using programmaticInterface's addProject()
    function.

    `True` is returned if the project could be created, `False` otherwise."""

    result = pI.addProject(name, extSchema)

    if result == pI.OperationResults.SUCCESS:
        return True
    return False
