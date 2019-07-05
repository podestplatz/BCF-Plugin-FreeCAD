from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot

class SimpleListModel(QAbstractListModel):
    def __init__(self, mlist):
        QAbstractListModel.__init__(self)

        # Cache the passed data list as a class member.
        self._items = mlist

    # We need to tell the view how many rows we have present in our data.
    # For us, at least, it's fairly straightforward, as we have a python list of data,
    # so we can just return the length of that list.
    def rowCount(self, parent = QModelIndex()):
        return len(self._items)


    def deleteFirst(self):
        if len(self._items) > 0:
            self.beginRemoveRows(QModelIndex(), 1, 1)
            self._items.pop(0)
            self.endRemoveRows()


    def data(self, index, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            # The view is asking for the actual data, so, just return the item it's asking for.
            return self._items[index.row()]

        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                return QColor("gray")
            else:
                return QColor("lightGray")

        elif role == Qt.EditRole:
            return self._items[index.row()]

        else:
            # We don't care about anything else, so make sure to return an empty QVariant.
            return None


    def setData(self, index, value, role = Qt.EditRole):

        if role == Qt.EditRole:
            self._items[index.row()] == str(value.toString().toUtf8)
            QObject.emit(self, SIGNAL("dataChanged(const QModelIndex&, const"\
                    "QModelIndex&)"), index, index)
            return True
        return False


    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled


    def removeRows(self, row, count, parent = QModelIndex()):
        if row < 0  or row > len(self._items):
            return

        self.beginRemoveRows(parent, row, row+count -1)
        while count != 0:
            del self._items[row]
            count -= 1
        self.endRemoveRows()


    def addItem(self, item):
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append(str(item))
        self.endInsertRows()

