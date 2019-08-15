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
        """ Currently set topic. """
        self.documents = []
        """ List of documents that are to be displayed. """


    def rowCount(self, parent = QModelIndex()):

        """ Returns the number of documents to be displayed. """

        return len(self.documents)


    def columnCount(self, parent = QModelIndex()):

        """ Returns the amount of columns needed.

        Two columns are needed. One for the name of the document and one for
        the path.
        """

        return 2 # external, description, reference


    def data(self, index, role = Qt.DisplayRole):

        """ Returns the either the path or the name of one the document depending
        on `index`.

        Special documents, ones whose path exists on the local system, will be
        colored as link. Documents not to be found on the system will be
        colored in the default text color.
        """

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

        """ Defines the two values for the horizontal header. """

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

        """ Either deletes the internal list of documents or retrieves a new
        one from `topic`.

        If `topic is None` then the list of documents will be deleted.
        Otherwise the list of associated documents to that topic is retrieved.
        """

        self.beginResetModel()

        if topic is None:
            self.documents = []
            self.topic = None

        else:
            self.createDocumentsList(topic)
            self.topic = topic

        self.endResetModel()


    def createDocumentsList(self, topic):

        """ Just creates an internal reference to `topic.docRefs`. """

        self.documents = topic.docRefs


    def getFilePath(self, index):

        """ Construct the file path of the document on `index`.

        Here a distinction between external and internal documents is made. For
        documents marked as internal the path to the working directory is
        prepended to the document's path. Otherwise the path is assumed to be
        absolute. The resulting path is to be returned.
        """

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
