from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot


class CommentModel(QAbstractListModel):


    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        self.items = [("This is a comment", "a@b.c", "2019-07-09T09:23:10", "",
            "")]*2


    @Slot()
    def resetItems(self):
        beginResetModel()
        self.items = [("This is a comment", "a@b.c", "2019-07-09T09:23:10", "",
            "")]
        endResetModel()


    def rowCount(self, parent = QModelIndex()):

        return len(self.items)


    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid() or (role != Qt.DisplayRole and
                role != Qt.EditRole):
            return None

        comment = None
        commentItem = self.items[index.row()]
        if role == Qt.DisplayRole:
            comment = (commentItem[0],
                    commentItem[1] if commentItem[3] == "" else commentItem[3],
                    commentItem[2] if commentItem[4] == "" else commentItem[4])

        elif role == Qt.EditRole: # date is automatically set when editing
            comment = (commentItem[0],
                    commentItem[1] if commentItem[3] == "" else commentItem[3])

        return comment


    def flags(self, index):

        fl = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return fl


    def setData(self, index, value, role=Qt.EditRole):
        # https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html#PySide2.QtCore.PySide2.QtCore.QAbstractItemModel.roleNames

        if not index.isValid() or role != Qt.EditRole:
            return False

        commentToEdit = self.items[index.row()]
        newComment = (value[0], commentToEdit[1], commentToEdit[2], value[1],
                commentToEdit[4])

        self.items.pop(index.row())
        self.items.insert(index.row(), newComment)
        return True

