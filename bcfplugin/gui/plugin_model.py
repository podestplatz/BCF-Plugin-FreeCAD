from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot
import bcfplugin.programmaticInterface as pI


def openProjectBtnHandler(file):
    pI.openProject(file)

def getProjectName():
    return pI.getProjectName()


class TopicCBModel(QAbstractListModel):

    def __init__(self):
        QAbstractListModel.__init__(self)
        self.updateTopics()
        self.items = []


    def updateTopics(self):

        if not pI.isProjectOpen():
            return

        topics = pI.getTopics()
        if topics != pI.OperationResults.FAILURE:
            self.items = [ topic[1].title for topic in topics ]
            self.items.insert(0, "-- Select your topic --")


    def rowCount(self, parent = QModelIndex()):
        return len(self.items)


    def data(self, index, role = Qt.DisplayRole):

        idx = index.row()
        if role == Qt.DisplayRole:
            return self.items[idx]

        else:
            return None


    def flags(self, index):
        flaggs = Qt.ItemIsEnabled
        if index.row() != 0:
            flaggs |= Qt.ItemIsSelectable
        return flaggs


    @Slot()
    def projectOpened(self):
        self.updateTopics()
