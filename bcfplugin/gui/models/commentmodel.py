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
This file provides the CommentModel. It provides the CommentList with a tuple
of three values per every row. For a description of these three values please
see the documentation below.
"""

import os
import copy
import logging

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


class CommentModel(QAbstractListModel):

    """ Model for the comment list.

    Ever comment item is comprised of three values:
        - the comment text itself,
        - the E-Mail address of the person that last modified it, or if it was
          not modified till now the one of the original creator, and
        - the date of the last modification, or creation if no modification has
          taken place.

    Also this model introduces the notion of a 'special comment'. A special
    comment is a comment object where the 'viewpoint' member references an
    actual instance of ViewpointReference.
    """

    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        self.items = []
        self.currentTopic = None


    def removeRow(self, index):

        """ Removes a comment at `index` from the model.

        `True` is returned if the comment could be deleted successfully,
        `False` is returned otherwise.
        If the deletion was successful the internal list of comments is
        refreshed.
        """

        if not index.isValid():
            return False

        self.beginRemoveRows(index, index.row(), index.row())
        idx = index.row()
        commentToRemove = self.items[idx]
        result = pI.deleteObject(commentToRemove)
        if result == pI.OperationResults.FAILURE:
            return False

        self.items.pop(idx)
        self.endRemoveRows()

        # load comments of the topic anew
        self.resetItems(self.currentTopic)
        return True


    def rowCount(self, parent = QModelIndex()):

        """ Returns the amount of comments that are stored in the model. """

        return len(self.items)


    def data(self, index, role=Qt.DisplayRole):

        """ Returns the data to be displayed by the comment view.

        A comment element returned is a tuple consisting of three elements:
            - the comment text itself,
            - the author of the last modification or of the creation if no
              modification has taken place
            - the date of the last modification or the creation respectively

        Per default the this function returns the brush used for drawing normal
        text. But special comments are drawn with the colour associated with
        links defined in the global colour palette.
        For example consider a light theme then the text colour of an ordinary
        comment would be plain old black and the text colour of a special
        comment would be the hyperlink blue (on a standard system). However
        these values are dependant on the current Qt theme that is configured.
        """

        if not index.isValid() or index.row() >= len(self.items):
            return None

        if (role != Qt.DisplayRole and
                role != Qt.EditRole and role != Qt.ForegroundRole):
            return None

        comment = None
        item = self.items[index.row()]
        commentText = ""
        commentAuthor = ""
        commentDate = ""

        commentText = item.comment.strip()
        if role == Qt.DisplayRole:
            # if modDate is set take the modDate and modAuthor, regardless of
            # the date and author values.
            if item.modDate != item._modDate.defaultValue:
                commentAuthor = item.modAuthor
                commentDate = str(item._modDate)
            else:
                commentAuthor = item.author
                commentDate = str(item._date)
            comment = (commentText, commentAuthor, commentDate)

        elif role == Qt.EditRole: # date is automatically set when editing
            commentAuthor = item.author if item.modAuthor == "" else item.modAuthor
            comment = (commentText, commentAuthor)

        elif role == Qt.ForegroundRole:
            # set the color if a viewpoint is linked to the comment
            link = QApplication.palette().link()
            normal = QApplication.palette().text()
            brush = normal if item.viewpoint is None else link

            return brush

        return comment


    def flags(self, index):

        """ Every comment shall be selectable, editable and be enabled.

        The modification of special comments does not alter the link between
        the comment and the instance of `ViewpointReference`.
        """

        fl = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return fl


    def setData(self, index, value, role=Qt.EditRole):
        # https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html#PySide2.QtCore.PySide2.QtCore.QAbstractItemModel.roleNames

        """ Updates a comment specified by `index` with the new `value`.

        `value` is assumed to be a tuple constructed by `CommentDelegate`.
        The first value contains the text of the comment, the second contains
        the email address of the author who did the modification.
        """

        if not index.isValid() or role != Qt.EditRole:
            return False

        commentToEdit = self.items[index.row()]
        commentToEdit.comment = value[0]
        commentToEdit.modAuthor = value[1]

        pI.modifyElement(commentToEdit, value[1])
        topic = pI.getTopic(commentToEdit)
        self.resetItems(topic)

        return True


    @Slot(Topic)
    def resetItems(self, topic = None):

        """ Either updates the internal list of comments depending on topic or
        deletes the internal list.

        If topic is set to `None` then all elements will be deleted from the
        model. Otherwise all comments of `topic` are retrieved and stored in
        `items`."""

        self.beginResetModel()

        if topic is None:
            del self.items
            self.items = list()
            self.endResetModel()
            return

        if not pI.isProjectOpen():
            util.showError("First you have to open a project.")
            logger.error("First you have to open a project.")
            self.endResetModel()
            return

        comments = pI.getComments(topic)
        if comments == pI.OperationResults.FAILURE:
            util.showError("Could not get any comments for topic" \
                    " {}".format(str(topic)))
            logger.error("Could not get any comments for topic" \
                    " {}".format(str(topic)))
            self.endResetModel()
            return

        self.items = [ comment[1] for comment in comments ]
        self.currentTopic = topic

        self.endResetModel()


    def addComment(self, value):

        """ Add a new comment to the items list and to the underlying data
        model using the programmaticInterface.

        For the addition the programmatic Interface is used. It creates a unique
        UUID for the comment, as well as it takes the current time stamp
        """

        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        success = pI.addComment(self.currentTopic, value[0], value[1], None)
        if success == pI.OperationResults.FAILURE:
            self.endInsertRows()
            return False

        self.endInsertRows()
        # load comments anew
        self.resetItems(self.currentTopic)

        return True


    def referencedViewpoint(self, index):

        """ Checks whether a comment is special or not. """

        if not index.isValid():
            return None

        return self.items[index.row()].viewpoint
