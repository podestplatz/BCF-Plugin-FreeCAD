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


    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        # holds a list of all topic objects referenced by the "relatedTopics"
        # list inside the current topic object `topic`
        self.relTopics = list()
        self.topic = None


    def flags(self, index):

        """ The resulting list shall only be read only.

        In the future however it is possible to also let the user add related
        topics.
        """

        flgs = Qt.ItemIsEnabled
        flgs |= Qt.ItemIsSelectable

        return flgs


    def rowCount(self, parent = QModelIndex()):

        return len(self.relTopics)


    def data(self, index, role = Qt.DisplayRole):

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

        self.beginResetModel()

        if topic is None:
            self.relTopics = list()
            self.topic = None

        else:
            self.createRelatedTopicsList(topic)
            self.topic = topic

        self.endResetModel()


    def createRelatedTopicsList(self, topic):

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

