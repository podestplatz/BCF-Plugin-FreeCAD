from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot, Qt

import bcfplugin.programmaticInterface as pI


class CommentModel(QAbstractListModel):


    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        self.items = []


    @Slot()
    def resetItems(self, topic):

        """ Load comments from `topic` """

        self.beginResetModel()

        if not pI.isProjectOpen():
            #TODO: display error
            self.endResetModel()
            return

        comments = pI.getComments(topic)
        if comments == pI.OperationResults.FAILURE:
            #TODO: display error
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

