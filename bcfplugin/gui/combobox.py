import sys
if __name__ == "__main__":
    sys.path.insert(0, "../")

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import QAbstractListModel, QModelIndex

from programmaticInterface import *


class ComboBoxModel(QAbstractListModel):

    def __init__(self):
        QAbstractListModel.__init__(self)

        topics = getTopics()
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



class MyMainWindow(QWidget):

    def __init__(self):

        QWidget.__init__(self)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        cbModel = ComboBoxModel()
        self.cb = QComboBox()
        self.cb.setModel(cbModel)
        self.topicLabel = QLabel("Topic")

        hbox.addWidget(self.topicLabel)
        hbox.addWidget(self.cb)

        vbox.addLayout(hbox)
        self.setLayout(vbox)


if __name__ == "__main__":
    openProject("../rdwr/test_data/Issues_BIMcollab_Example.bcf")
    app = QApplication(sys.argv)
    w = MyMainWindow()
    w.show()
    app.exec_()
    sys.exit()

