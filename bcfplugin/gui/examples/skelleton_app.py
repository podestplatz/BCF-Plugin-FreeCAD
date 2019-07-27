import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot
from skelleton_model import SimpleListModel
from skelleton_view import SimpleListView

class MyMainWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self, None)

        # main section of the window
        vbox = QVBoxLayout()

        # create a data source:
        self._model = SimpleListModel(["test", "tes1t", "t3est", "t5est", "t3est"])

        # let's add two views of the same data source we just created:
        v = SimpleListView()
        v.setModel(self._model)
        vbox.addWidget(v)

        # second view..
        v = SimpleListView()
        v.setModel(self._model)
        vbox.addWidget(v)

        # bottom section of the window
        hbox = QHBoxLayout()
        self._itemedit = QLineEdit()

        btn = QPushButton("Add Item!")
        btn.clicked.connect(self.doAddItem)

        hbox.addWidget(self._itemedit)
        hbox.addWidget(btn)

        # add bottom to main window layout
        vbox.addLayout(hbox)

        # set layout on the window
        self.setLayout(vbox)

    @Slot()
    def doAddItem(self):
        self._model.addItem(self._itemedit.text())
        self._itemedit.setText("")


# set things up, and run it. :)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyMainWindow()
    w.show()
    app.exec_()
    sys.exit()  # colours depending.
