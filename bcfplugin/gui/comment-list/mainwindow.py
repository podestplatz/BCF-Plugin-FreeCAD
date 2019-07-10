import sys
if __name__ == "__main__":
    sys.path.insert(0, "../../..")
    import bcfplugin.programmaticInterface as pI
    import bcfplugin.util as util

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot

from commentmodel import CommentModel
from commentdelegate import CommentDelegate


class MainWindow(QWidget):

    def __init__(self):

        QWidget.__init__(self, None)

        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        self.commentList = QListView()

        commentDelegate = CommentDelegate()
        self.commentList.setItemDelegate(commentDelegate)
        self.commentList.doubleClicked.connect(self.editEvent)

        topic = pI.getTopics()[0]
        commentModel = CommentModel()
        commentModel.resetItems(topic[1])
        self.commentList.setModel(commentModel)

        vboxLayout.addWidget(self.commentList)


    def editEvent(self, index):

        self.commentList.edit(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pI.openProject("../../rdwr/test_data/Issues_BIMcollab_Example.bcf")

    widget = MainWindow()
    widget.show()

    app.exec_()
    sys.exit()

