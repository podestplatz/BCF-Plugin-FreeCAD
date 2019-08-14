import os
import copy
import logging
from uuid import uuid4

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QAbstractTableModel,
        QModelIndex, Slot, Signal, Qt, QSize)

import bcfplugin
import bcfplugin.programmaticInterface as pI
import bcfplugin.util as util
from bcfplugin.rdwr.topic import Topic
from bcfplugin.rdwr.markup import Comment

logger = bcfplugin.createLogger(__name__)


class AdditionalDocumentsModel(QAbstractTableModel):

    """ Model intended to supply a table view with data about the additional
    document references of a topic.

    As with comments, here also the notion of a special reference is
    introduced. A special reference is one whose associated path does exist on
    the local system. It thus is painted in blue. Other references are painted
    in black.
    """

    def __init__(self, parent = None):

        QAbstractTableModel.__init__(self, parent)
        self.topic = None
        self.documents = []


    def rowCount(self, parent = QModelIndex()):

        return len(self.documents)


    def columnCount(self, parent = QModelIndex()):

        return 2 # external, description, reference


    def data(self, index, role = Qt.DisplayRole):

        if not index.isValid():
            return None

        ret_val = None
        if role == Qt.DisplayRole:
            if index.column() == 0:
                ret_val = self.documents[index.row()].description
            elif index.column() == 1:
                ret_val = str(self.documents[index.row()].reference)

        path = self.getFilePath(index)
        isPath = os.path.exists(path)
        if role == Qt.ForegroundRole:
            brush = QApplication.palette().text()
            if index.column() == 0:
                if isPath:
                    brush = QApplication.palette().link()

            ret_val = brush

        return ret_val


    def headerData(self, section, orientation, role = Qt.DisplayRole):

        if role != Qt.DisplayRole:
            return None

        header = None
        if orientation == Qt.Horizontal:
            if section == 0:
                header = "Description"
            elif section == 1:
                header = "Path"

        return header


    @Slot()
    def resetItems(self, topic = None):

        self.beginResetModel()

        if topic is None:
            self.documents = []
            self.topic = None

        else:
            self.createDocumentsList(topic)
            self.topic = topic

        self.endResetModel()


    def createDocumentsList(self, topic):

        self.documents = topic.docRefs


    def getFilePath(self, index):

        global bcfDir

        if not index.isValid():
            return None

        if index.row() >= len(self.documents):
            return None

        doc = self.documents[index.row()]
        path = str(doc.reference)
        if not doc.external:
            sysTmp = util.getBcfDir()
            path = os.path.join(sysTmp, path)

        return path
