import sys
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot

class MyMainWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self, None)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")

        self.projectGroup = QGroupBox()
        self.projectGroup.setEnabled(True)
        self.projectGroup.setObjectName("projectGroup")

        self.projectLayout = QHBoxLayout(self.projectGroup)
        self.projectLayout.setObjectName("projectLayout")

        self.projectLabel = QLabel("Open Project")
        self.projectLabel.setObjectName("projectLabel")
        self.projectLayout.addWidget(self.projectLabel)

        self.projectButton = QPushButton("Open")
        self.projectButton.setObjectName("projectButton")
        self.projectLayout.addWidget(self.projectButton)

        self.mainLayout.addWidget(self.projectGroup)
        self.setLayout(self.mainLayout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    plugin = MyMainWindow()
    plugin.show()

    app.exec_()
    sys.exit()
