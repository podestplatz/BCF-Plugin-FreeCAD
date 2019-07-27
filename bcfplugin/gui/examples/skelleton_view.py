from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot
import sys

class SimpleListView(QListView):
    def __init__(self, parent = None):
        QListView.__init__(self, parent)

        self.setAlternatingRowColors(True)

        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        deleteSel = QAction("Delete Selected", self)
        deleteFirst = QAction("Delete First", self)

        deleteSel.triggered.connect(self.deleteSelectedHandler)
        deleteFirst.triggered.connect(self.deleteFirstHandler)

        self.addAction(deleteSel)
        self.addAction(deleteFirst)

    @Slot()
    def deleteSelectedHandler(self):
        self.model().removeRows(self.currentIndex().row(), 1)

    @Slot()
    def deleteFirstHandler(self):
        self.model().deleteFirst()

