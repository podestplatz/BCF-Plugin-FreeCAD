from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot, Signal

import bcfplugin.programmaticInterface as pI
from bcfplugin.rdwr.topic import Topic


def openProjectBtnHandler(file):
    pI.openProject(file)

def getProjectName():
    return pI.getProjectName()


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


    @Slot(Topic)
    def resetItems(self, topic):

        """ Load comments from `topic` """

        self.beginResetModel()

        if not pI.isProjectOpen():
            util.showError("First you have to open a project.")
            self.endResetModel()
            return

        comments = pI.getComments(topic)
        if comments == pI.OperationResults.FAILURE:
            util.showError("Could not get any comments for topic" \
                    " {}".format(str(topic)))
            self.endResetModel()
            return

        self.items = [ comment[1] for comment in comments ]

        self.endResetModel()


    def rowCount(self, parent = QModelIndex()):

        return len(self.items)


    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid() or (role != Qt.DisplayRole and
                role != Qt.EditRole):
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
            commentDate = (item.date if item.modDate == "" else item.modDate)
            commentDate = commentDate.strftime(dateFormat)
            comment = (commentText, commentAuthor, commentDate)

        elif role == Qt.EditRole: # date is automatically set when editing
            commentText = item.comment
            commentAuthor = item.author if item.modAuthor == "" else item.modAuthor
            comment = (commentText, commentAuthor)

        return comment


    def flags(self, index):

        fl = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return fl


    def setData(self, index, value, role=Qt.EditRole):
        # https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html#PySide2.QtCore.PySide2.QtCore.QAbstractItemModel.roleNames

        if not index.isValid() or role != Qt.EditRole:
            return False

        commentToEdit = self.items[index.row()]
        commentToEdit.comment = value[0]
        commentToEdit.modAuthor = value[1]

        pI.modifyElement(commentToEdit, value[1])
        topic = pI.getTopic(commentToEdit)
        self.resetItems(topic)

        return True

