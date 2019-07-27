import os

from PySide2.QtCore import (QSize, QAbstractListModel, Qt, QModelIndex, QPoint,
        Slot)
from PySide2.QtGui import QImageReader, QPixmap, QRegion
from PySide2.QtWidgets import (QHBoxLayout, QLabel, QSizePolicy, QFrame,
        QMessageBox, QListView, QListWidget, QStyledItemDelegate, QWidget)

def tr(text):

    """ Placeholder for translation """

    return text


class SnapshotModel(QAbstractListModel):

    PIC1 = "./resources/snapshot1.jpg"
    PIC2 = "./resources/snapshot2.jpg"
    PIC3 = "./resources/snapshot3.png"

    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        self.size = QSize(100, 100)


    def data(self, index, role = Qt.DisplayRole):

        if not index.isValid():
            return None

        if not role == Qt.DecorationRole:
            return None


        img = None
        if index.row() == 0:
            img = self.loadImage(SnapshotModel.PIC1)
        elif index.row() == 1:
            img = self.loadImage(SnapshotModel.PIC2)
        elif index.row() == 2:
            img = self.loadImage(SnapshotModel.PIC3)

        if img is None:
            return None

        img = img.scaled(self.size, Qt.KeepAspectRatio)
        return img


    def rowCount(self, parent = QModelIndex()):

        if __name__ == "__main__":
            return 3
        return int(len(self.items) / 3)


    def loadImage(self, path):

        """ Load the image behind `path` into `imgContainer` """
        if not os.path.exists(path):
            QMessageBox.information(None, tr("Image Load"), tr("The image {}"\
                    " could not be found.".format(path)),
                    QMessageBox.Ok)
            return None

        imgReader = QImageReader(path)
        imgReader.setAutoTransform(True)
        img = imgReader.read()
        if img.isNull():
            QMessageBox.information(None, tr("Image Load"), tr("The image {}"\
                    " could not be loaded. Skipping it then.".format(path)),
                    QMessageBox.Ok)
            return None

        return QPixmap.fromImage(img)


    def setSize(self, newSize: QSize):

        """ Sets the size in which the Pixmaps are returned """

        self.size = newSize


class SnapshotView(QListView):

    def __init__(self, parent = None):

        QListView.__init__(self, parent)
        self.minIconSize = QSize(100, 100)


    def resizeEvent(self, event):

        newSize = self.size()
        print("New widget size is: {}".format(newSize))
        newItemWidth = newSize.width() / self.model().rowCount()
        newItemWidth -= (self.model().rowCount() - 1) * self.spacing()
        newItemSize = QSize(newItemWidth, newSize.height())

        if (newItemWidth < self.minIconSize.width()):
            newItemSize.setWidth(self.minIconSize.width())
        elif (newItemSize.height() < self.minIconSize.height()):
            newItemSize.setHeight(self.minIconSize.height())

        self.model().setSize(newItemSize)
        self.setIconSize(newItemSize)
        QListView.resizeEvent(self, event)


if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication

    app = QApplication(sys.argv)
    snModel = SnapshotModel()
    snView = SnapshotView()
    snView.setFlow(QListView.Flow.LeftToRight)
    snView.setSpacing(5)
    #snView.setGridSize(QSize(1, 3))
    snView.setModel(snModel)
    #snView.setItemDelegate(snDelegate)
    snView.show()
    app.exec_()
    sys.exit()
