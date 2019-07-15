from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot, Signal, Qt

import bcfplugin.programmaticInterface as pI
import bcfplugin.util as util

from uuid import uuid4
from bcfplugin.rdwr.topic import Topic
from bcfplugin.rdwr.markup import Comment


def openProjectBtnHandler(file):

    """ Handler of the "Open" button for a project """

    pI.openProject(file)


def getProjectName():

    """ Wrapper for programmaticInterface.getProjectName() """

    return pI.getProjectName()


def saveProject(dstFile):

    """ Wrapper for programmaticInterface.saveProject() """

    pI.saveProject(dstFile)


class TopicCBModel(QAbstractListModel):

    selectionChanged = Signal((Topic,))

    def __init__(self):
        QAbstractListModel.__init__(self)
        self.updateTopics()
        self.items = []


    def updateTopics(self):

        self.beginResetModel()

        if not pI.isProjectOpen():
            self.endResetModel()
            return

        topics = pI.getTopics()
        if topics != pI.OperationResults.FAILURE:
            self.items = [ topic[1] for topic in topics ]

        self.endResetModel()


    def rowCount(self, parent = QModelIndex()):
        return len(self.items) + 1 # plus the dummy element


    def data(self, index, role = Qt.DisplayRole):

        idx = index.row()
        if role == Qt.DisplayRole:
            if idx == 0:
                return "-- Select your topic --"
            return self.items[idx - 1].title # subtract the dummy element

        else:
            return None


    def flags(self, index):
        flaggs = Qt.ItemIsEnabled
        if index.row() != 0:
            flaggs |= Qt.ItemIsSelectable
        return flaggs


    @Slot(int)
    def newSelection(self, index):

        if index > 0: # 0 is the dummy element
            self.selectionChanged.emit(self.items[index - 1])


    @Slot()
    def projectOpened(self):
        self.updateTopics()


class CommentModel(QAbstractListModel):

    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        self.items = []
        self.currentTopic = None


    @Slot(Topic)
    def resetItems(self, topic = None):

        """ Load comments from `topic`.

        If topic is set to `None` then all elements will be deleted from the
        model."""

        self.beginResetModel()

        if topic is None:
            del self.items
            self.items = list()
            self.endResetModel()
            return

        if not pI.isProjectOpen():
            util.showError("First you have to open a project.")
            util.printError("First you have to open a project.")
            self.endResetModel()
            return

        comments = pI.getComments(topic)
        if comments == pI.OperationResults.FAILURE:
            util.showError("Could not get any comments for topic" \
                    " {}".format(str(topic)))
            util.printError("Could not get any comments for topic" \
                    " {}".format(str(topic)))
            self.endResetModel()
            return

        self.items = [ comment[1] for comment in comments ]
        self.currentTopic = topic

        self.endResetModel()


    def removeRow(self, index):

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

        return len(self.items)


    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid() or (role != Qt.DisplayRole and
                role != Qt.EditRole and role != Qt.ForegroundRole):
            return None

        comment = None
        item = self.items[index.row()]
        commentText = ""
        commentAuthor = ""
        commentDate = ""
        dateFormat = "%Y-%m-%d %X"
        if role == Qt.DisplayRole:
            commentText = item.comment
            commentAuthor = item.author if item.modAuthor == "" else item.modAuthor
            commentDate = (item.date if item.modDate == item._modDate.defaultValue else item.modDate)
            commentDate = commentDate.strftime(dateFormat)
            comment = (commentText, commentAuthor, commentDate)

        elif role == Qt.EditRole: # date is automatically set when editing
            commentText = item.comment
            commentAuthor = item.author if item.modAuthor == "" else item.modAuthor
            comment = (commentText, commentAuthor)

        elif role == Qt.ForegroundRole:
            # set the color if a viewpoint is linked to the comment
            white = QColor("black")
            vpCol = QColor("blue")
            col = white if item.viewpoint is None else vpCol
            brush = QBrush()
            brush.setColor(col)

            return brush

        return comment


    def flags(self, index):

        fl = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return fl


    def checkValue(self, text):

        splitText = [ textItem.strip() for textItem in text.split("--") ]
        if len(splitText) != 2:
            return None

        return splitText


    def setData(self, index, value, role=Qt.EditRole):
        # https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html#PySide2.QtCore.PySide2.QtCore.QAbstractItemModel.roleNames

        if not index.isValid() or role != Qt.EditRole:
            return False

        splitText = self.checkValue(value)
        if not splitText:
            return False

        commentToEdit = self.items[index.row()]
        commentToEdit.comment = splitText[0]
        commentToEdit.modAuthor = splitText[1]

        pI.modifyElement(commentToEdit, splitText[1])
        topic = pI.getTopic(commentToEdit)
        self.resetItems(topic)

        return True


    def addComment(self, value):

        """ Add a new comment to the items list.

        For the addition the programmatic Interface is used. It creates a unique
        UUID for the comment, as well as it takes the current time stamp
        """

        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        splitText = self.checkValue(value)
        if not splitText:
            self.endInsertRows()
            return False

        success = pI.addComment(self.currentTopic, splitText[0], splitText[1], None)
        if success == pI.OperationResults.FAILURE:
            self.endInsertRows()
            return False

        self.endInsertRows()
        # load comments anew
        self.resetItems(self.currentTopic)

        return True


