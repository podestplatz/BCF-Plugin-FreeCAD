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


class TopicListModel(QAbstractListModel):

    """ Model for the list view displaying the topics. """

    selectionChanged = Signal((Topic,))
    """ Signal emitted when a new topic was selected. """

    def __init__(self):

        QAbstractListModel.__init__(self)
        self.updateTopics()
        self.items = []


    def rowCount(self, parent = QModelIndex()):
        """ Returns the number of items the model is able to supply. """

        return len(self.items)


    def data(self, index, role = Qt.DisplayRole):

        """ Function used for retrieving data to display. """

        idx = index.row()
        if role == Qt.DisplayRole:
            return self.items[idx].title

        else:
            return None


    def flags(self, index):

        """ Function defining that all elements shall be selectable and
        enabled. """

        flaggs = Qt.ItemIsEnabled
        flaggs |= Qt.ItemIsSelectable

        return flaggs


    @Slot()
    def updateTopics(self):

        """ Updates the internal list of topics. """

        self.beginResetModel()

        if not pI.isProjectOpen():
            self.endResetModel()
            return

        topics = pI.getTopics()
        if topics != pI.OperationResults.FAILURE:
            self.items = [ topic[1] for topic in topics ]

        self.endResetModel()


    @Slot(int)
    def newSelection(self, index):

        """ Handler invoked when a new topic in the list was double clicked.
        """

        if index.row() >= 0: # 0 is the dummy element
            self.selectionChanged.emit(self.items[index.row()])


