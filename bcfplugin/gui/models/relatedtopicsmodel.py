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

import logging

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QAbstractTableModel,
        QModelIndex, Slot, Signal, Qt, QSize)

import bcfplugin
import bcfplugin.programmaticInterface as pI
import bcfplugin.util as util
from bcfplugin.rdwr.topic import Topic

logger = bcfplugin.createLogger(__name__)


class RelatedTopicsModel(QAbstractListModel):

    """ Model managing data behind the related topics list in topic metrics
    dialog. """

    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        # holds a list of all topic objects referenced by the "relatedTopics"
        # list inside the current topic object `topic`
        self.relTopics = list()
        """ List of instances of `Topic` that are specified as related to
        `self.topic` """
        self.topic = None
        """ Current topic to which the related topics shall be displayed. """


    def flags(self, index):

        """ The resulting list shall only be read only.

        In the future however it is possible to also let the user add related
        topics.
        """

        flgs = Qt.ItemIsEnabled
        flgs |= Qt.ItemIsSelectable

        return flgs


    def rowCount(self, parent = QModelIndex()):

        """ Returns the amount of topics related to `self.topic`. """

        return len(self.relTopics)


    def data(self, index, role = Qt.DisplayRole):

        """ Returns the title of the Nth topic (defined by `index`) related to
        `self.topic`. """

        if not index.isValid():
            return None

        if index.row() >= len(self.relTopics):
            logger.info("A too large index was passed! Please report the"\
                    " steps you did as issue on the plugin's github page.")
            return None

        if role != Qt.DisplayRole:
            return None

        idx = index.row()
        topicTitle = self.relTopics[idx].title

        return topicTitle


    @Slot()
    def resetItems(self, topic = None):

        """ Either resets the internal state or retrieves related topics to
        `topic`.

        If `topic is None` the internal list `self.relTopics` is deleted.
        Otherwise a list of related topics to `topic` is constructed.
        """

        self.beginResetModel()

        if topic is None:
            del self.relTopics
            self.relTopics = list()
            self.topic = None

        else:
            self.createRelatedTopicsList(topic)
            self.topic = topic

        self.endResetModel()


    def createRelatedTopicsList(self, topic):

        """ Compiles a list of `Topic` instances based on a list of UUIDs.

        An instance of `Topic` has a list of UUIDs, each specifying one related
        topic. This function now searches in the data model for each of these
        UUIDs and stores a reference to the corresponding `Topic` instance in
        `relatedTopics` and returns the result.
        """

        if topic is None:
            return False

        relatedTopics = topic.relatedTopics
        for t in relatedTopics:
            # in this list only the uid of a topic is stored
            tUId = t.value
            logger.debug("Getting topic to: {}:{}".format(tUId, tUId.__class__))
            match = pI.getTopicFromUUID(tUId)
            if match != pI.OperationResults.FAILURE:
                self.relTopics.append(match)
                logger.debug("Got a match {}".format(match.title))
            else:
                logger.debug("Got nothing back")

