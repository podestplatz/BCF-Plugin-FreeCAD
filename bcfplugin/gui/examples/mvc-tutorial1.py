import sys

from PySide2.QtGui import QColor
from PySide2.QtWidgets import (QApplication, QListView, QWidget, QVBoxLayout,
        QHBoxLayout)
from PySide2.QtCore import QAbstractListModel, QModelIndex, Qt


class SimpleListModel(QAbstractListModel):

    def __init__(self, initList):

        QAbstractListModel.__init__(self)
        self._items = initList


    def rowCount(self, parent = QModelIndex()):

        return len(self._items)


    def data(self, index, role = Qt.DisplayRole):

        if role == Qt.DisplayRole:
            return self._items[index.row()]
        elif role == Qt.BackgroundRole:
            if index.row() % 2 == 0:
                return QColor("gray")
            else:
                return QColor("lightGray")
        else:
            return None


class SimpleListView(QListView):

    def __init__(self, parent = None):

        QListView.__init__(self, parent)


class MyMainWindow(QWidget):

    def __init__(self):

        QWidget.__init__(self, None) # no parent, display as window
        vbox = QVBoxLayout()
        m = SimpleListModel(["hallo", "du", "wie", "geht", "es", "dir",
            "heute"])

        # add first view
        v = SimpleListView()
        v.setModel(m)
        vbox.addWidget(v)

        # add second view with the same model
        v = SimpleListView()
        v.setModel(m)
        vbox.addWidget(v)

        # doesn't do much yet
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        self.setLayout(vbox)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyMainWindow()
    w.show()
    app.exec_()
    sys.exit()
