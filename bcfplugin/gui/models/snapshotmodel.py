import os
import copy
import logging
from uuid import uuid4

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QAbstractTableModel,
        QModelIndex, Slot, Signal, Qt, QSize)

import bcfplugin
import bcfplugin.programmaticInterface as pI
import bcfplugin.util as util
from bcfplugin.rdwr.topic import Topic
from bcfplugin.rdwr.markup import Comment

logger = bcfplugin.createLogger(__name__)


class SnapshotModel(QAbstractListModel):

    """ Model only returning picutes.

    It is intended for a list that only shows the icons and no text.
    Every image returned is scaled down to 100x100 pixels.
    Since the loading of images can be resource intensive, a lazy loading
    approach is followed here.
    """

    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)

        self.size = QSize(100, 100)
        """ Size of an icon """
        self.currentTopic = None
        """ Currently open topic """
        self.snapshotList = []
        """ List of the snapshot files """
        self.snapshotImgs = []
        """ Buffer of the already loaded images """


    def data(self, index, role = Qt.DisplayRole):

        """ Only implements the DecorationRole and returns images scaled to
        100x100 pixels.

        The images itself are returned as instances of QPixmap.
        """

        if not index.isValid():
            return None

        # only return icons.
        if not role == Qt.DecorationRole:
            return None

        # lazy loading images into `self.snapshotImgs`
        if self.snapshotImgs[index.row()] is None:
            img = self.loadImage(self.snapshotList[index.row()])
            self.snapshotImgs[index.row()] = img

        img = self.snapshotImgs[index.row()]
        if img is None: # happens if the image could not be loaded
            return None

        # scale image to currently set size
        img = img.scaled(self.size, Qt.KeepAspectRatio)
        return img


    def rowCount(self, parent = QModelIndex()):

        """ Returns the amount of items the model can return, capped at three
        items """

        return len(self.snapshotList) if len(self.snapshotList) < 3 else 3


    def setSize(self, newSize: QSize):

        """ Sets the size in which the Pixmaps are returned """

        self.size = newSize


    @Slot()
    def resetItems(self, topic = None):

        """ Reset the internal state of the model.

        If `topic` != None then the snapshots associated with the new topic are
        loaded, else the list of snapshots is cleared.
        """

        self.beginResetModel()

        if topic is None:
            self.snapshotList = []
            self.endResetModel()
            return

        self.currentTopic = topic
        snapshots = pI.getSnapshots(self.currentTopic)
        if snapshots == pI.OperationResults.FAILURE:
            self.snapshotList = []
            return

        self.snapshotList = snapshots
        # clear the image buffer
        self.snapshotImgs = [None]*len(snapshots)
        self.endResetModel()


    def imgFromFilename(self, filename: str):

        """ Returns the image with `filename`. It is loaded if it isn't at the
        point of inquiry.

        The image is returned in original resolution. The user is responsible
        for scaling it to the desired size.
        """

        filenameList = [ os.path.basename(path) for path in self.snapshotList ]
        if filename not in filenameList:
            return None

        idx = filenameList.index(filename)
        if self.snapshotImgs[idx] is None:
            img = self.loadImage(self.snapshotList[idx])
            self.snapshotImgs[idx] = img

        img = self.snapshotImgs[idx]
        if img is None: # image could not be loaded (FileNotFoundError?)
            return None

        return img


    def realImage(self, index):

        """ Return the image at `index` in original resolution """

        if not index.isValid():
            return None

        if (index.row() > len(self.snapshotImgs) or
                self.snapshotImgs[index.row()] is None):
            return None

        img = self.snapshotImgs[index.row()]
        return img


    def loadImage(self, path: str):

        """ Load the image from `path` and return a QPixmap """

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


