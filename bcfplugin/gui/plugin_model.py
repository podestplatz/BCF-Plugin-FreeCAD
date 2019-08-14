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
from bcfplugin.frontend.viewController import CamType

logger = bcfplugin.createLogger(__name__)


def openProjectBtnHandler(file):

    """ Handler of the "Open" button for a project """

    pI.openProject(file)


def getProjectName():

    """ Wrapper for programmaticInterface.getProjectName() """

    return pI.getProjectName()


def saveProject(dstFile):

    """ Wrapper for programmaticInterface.saveProject() """

    pI.saveProject(dstFile)


def addTopic(newTopic: dict):

    """ Adds a topic to the internal data model by using
    programmaticInterface's addTopic() function """

    result = pI.addTopic(newTopic["title"], newTopic["author"],
            newTopic["type"], newTopic["description"], newTopic["status"],
            newTopic["priority"], newTopic["index"], newTopic["labels"],
            newTopic["dueDate"], newTopic["assignee"], newTopic["stage"])

    if result == pI.OperationResults.FAILURE:
        return False
    return True


def createProject(name: str, extSchema: str):

    """ Creates a new project by using programmaticInterface's addProject()
    function.

    `True` is returned if the project could be created, `False` otherwise."""

    result = pI.addProject(name, extSchema)

    if result == pI.OperationResults.SUCCESS:
        return True
    return False


class TopicListModel(QAbstractListModel):

    """ Model for the list view displaying the topics. """

    selectionChanged = Signal((Topic,))
    """ Signal emitted when a new topic was selected. """

    def __init__(self):

        QAbstractListModel.__init__(self)
        self.updateTopics()
        self.items = []


    def rowCount(self, parent = QModelIndex()):
        """ Returns the number of items the model is able to supply. """

        return len(self.items)


    def data(self, index, role = Qt.DisplayRole):

        """ Function used for retrieving data to display. """

        idx = index.row()
        if role == Qt.DisplayRole:
            return self.items[idx].title

        else:
            return None


    def flags(self, index):

        """ Function defining that all elements shall be selectable and
        enabled. """

        flaggs = Qt.ItemIsEnabled
        flaggs |= Qt.ItemIsSelectable

        return flaggs


    @Slot()
    def updateTopics(self):

        """ Updates the internal list of topics. """

        self.beginResetModel()

        if not pI.isProjectOpen():
            self.endResetModel()
            return

        topics = pI.getTopics()
        if topics != pI.OperationResults.FAILURE:
            self.items = [ topic[1] for topic in topics ]

        self.endResetModel()


    @Slot(int)
    def newSelection(self, index):

        """ Handler invoked when a new topic in the list was double clicked.
        """

        if index.row() >= 0: # 0 is the dummy element
            self.selectionChanged.emit(self.items[index.row()])


class CommentModel(QAbstractListModel):

    """ Model for the comment list.

    Ever comment item is comprised of three values:
        - the comment text itself,
        - the E-Mail address of the person that last modified it, or if it was
          not modified till now the one of the original creator, and
        - the date of the last modification, or creation if no modification has
          taken place.

    Also this model introduces the notion of a 'special comment'. A special
    comment is a comment object where the 'viewpoint' member references an
    actual instance of ViewpointReference.
    """

    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        self.items = []
        self.currentTopic = None


    def removeRow(self, index):

        """ Removes a comment at `index` from the model.

        `True` is returned if the comment could be deleted successfully,
        `False` is returned otherwise.
        If the deletion was successful the internal list of comments is
        refreshed.
        """

        if not index.isValid():
            return False

        self.beginRemoveRows(index, index.row(), index.row())
        idx = index.row()
        commentToRemove = self.items[idx]
        result = pI.deleteObject(commentToRemove)
        if result == pI.OperationResults.FAILURE:
            return False

        self.items.pop(idx)
        self.endRemoveRows()

        # load comments of the topic anew
        self.resetItems(self.currentTopic)
        return True


    def rowCount(self, parent = QModelIndex()):

        """ Returns the amount of comments that are stored in the model. """

        return len(self.items)


    def data(self, index, role=Qt.DisplayRole):

        """ Returns the data to be displayed by the comment view.

        A comment element returned is a tuple consisting of three elements:
            - the comment text itself,
            - the author of the last modification or of the creation if no
              modification has taken place
            - the date of the last modification or the creation respectively

        Per default the this function returns the brush used for drawing normal
        text. But special comments are drawn with the colour associated with
        links defined in the global colour palette.
        For example consider a light theme then the text colour of an ordinary
        comment would be plain old black and the text colour of a special
        comment would be the hyperlink blue (on a standard system). However
        these values are dependant on the current Qt theme that is configured.
        """

        if not index.isValid() or index.row() >= len(self.items):
            return None

        if (role != Qt.DisplayRole and
                role != Qt.EditRole and role != Qt.ForegroundRole):
            return None

        comment = None
        item = self.items[index.row()]
        commentText = ""
        commentAuthor = ""
        commentDate = ""

        commentText = item.comment.strip()
        if role == Qt.DisplayRole:
            # if modDate is set take the modDate and modAuthor, regardless of
            # the date and author values.
            if item.modDate != item._modDate.defaultValue:
                commentAuthor = item.modAuthor
                commentDate = str(item._modDate)
            else:
                commentAuthor = item.author
                commentDate = str(item._date)
            comment = (commentText, commentAuthor, commentDate)

        elif role == Qt.EditRole: # date is automatically set when editing
            commentAuthor = item.author if item.modAuthor == "" else item.modAuthor
            comment = (commentText, commentAuthor)

        elif role == Qt.ForegroundRole:
            # set the color if a viewpoint is linked to the comment
            link = QApplication.palette().link()
            normal = QApplication.palette().text()
            brush = normal if item.viewpoint is None else link

            return brush

        return comment


    def flags(self, index):

        """ Every comment shall be selectable, editable and be enabled.

        The modification of special comments does not alter the link between
        the comment and the instance of `ViewpointReference`.
        """

        fl = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return fl


    def setData(self, index, value, role=Qt.EditRole):
        # https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractItemModel.html#PySide2.QtCore.PySide2.QtCore.QAbstractItemModel.roleNames

        """ Updates a comment specified by `index` with the new `value`.

        `value` is assumed to be a tuple constructed by `CommentDelegate`.
        The first value contains the text of the comment, the second contains
        the email address of the author who did the modification.
        """

        if not index.isValid() or role != Qt.EditRole:
            return False

        commentToEdit = self.items[index.row()]
        commentToEdit.comment = value[0]
        commentToEdit.modAuthor = value[1]

        pI.modifyElement(commentToEdit, value[1])
        topic = pI.getTopic(commentToEdit)
        self.resetItems(topic)

        return True


    @Slot(Topic)
    def resetItems(self, topic = None):

        """ Either updates the internal list of comments depending on topic or
        deletes the internal list.

        If topic is set to `None` then all elements will be deleted from the
        model. Otherwise all comments of `topic` are retrieved and stored in
        `items`."""

        self.beginResetModel()

        if topic is None:
            del self.items
            self.items = list()
            self.endResetModel()
            return

        if not pI.isProjectOpen():
            util.showError("First you have to open a project.")
            logger.error("First you have to open a project.")
            self.endResetModel()
            return

        comments = pI.getComments(topic)
        if comments == pI.OperationResults.FAILURE:
            util.showError("Could not get any comments for topic" \
                    " {}".format(str(topic)))
            logger.error("Could not get any comments for topic" \
                    " {}".format(str(topic)))
            self.endResetModel()
            return

        self.items = [ comment[1] for comment in comments ]
        self.currentTopic = topic

        self.endResetModel()


    def addComment(self, value):

        """ Add a new comment to the items list and to the underlying data
        model using the programmaticInterface.

        For the addition the programmatic Interface is used. It creates a unique
        UUID for the comment, as well as it takes the current time stamp
        """

        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        success = pI.addComment(self.currentTopic, value[0], value[1], None)
        if success == pI.OperationResults.FAILURE:
            self.endInsertRows()
            return False

        self.endInsertRows()
        # load comments anew
        self.resetItems(self.currentTopic)

        return True


    def referencedViewpoint(self, index):

        """ Checks whether a comment is special or not. """

        if not index.isValid():
            return None

        return self.items[index.row()].viewpoint


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

        if (index.row() > len(self.snapshotImgs.keys()) or
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


class ViewpointsListModel(QAbstractListModel):

    """
    Model class to the viewpoins list.

    It returns the name of a viewpoint, associated with the current topic as
    well as an icon of the snapshot file that is referenced in the viewpoint. If
    no snapshot is referenced then no icon is returned.  An icon is 10x10
    millimeters in dimension. The actual sizes and offsets, in pixels, are
    stored in variables containing 'Q'. All other sizes and offset variables
    hold values in millimeters.These sizes and offsets are scaled to the
    currently active screen, retrieved by `util.getCurrentQScreen()`.
    """

    def __init__(self, snapshotModel, parent = None):

        QAbstractListModel.__init__(self, parent = None)
        self.viewpoints = []
        """ List of instances of `ViewpointReference` """
        # used to retrieve the snapshot icons.
        self.snapshotModel = snapshotModel
        """ Reference to SnapshotModel used to retrieve icons of the snapshots
        """

        # set up the sizes and offsets
        self._iconQSize = None
        """ Size in pixels """
        self._iconSize = QSize(10, 10)
        """ Size in millimeters """
        self.calcSizes()


    def data(self, index, role = Qt.DisplayRole):

        """ Returns the file name and an icon of the snapshot associated to a
        viewpoint. """

        if not index.isValid():
            return None

        viewpoint = self.viewpoints[index.row()]
        if role == Qt.DisplayRole:
            # return the name of the viewpoints file
            return str(viewpoint.file) + " (" + str(viewpoint.id) + ")"

        elif role == Qt.DecorationRole:
            # if a snapshot is linked, return an icon of it.
            filename = str(viewpoint.snapshot)
            icon = self.snapshotModel.imgFromFilename(filename)
            if icon is None: # snapshot is not listed in markup and cannot be loaded
                return None

            scaledIcon = icon.scaled(self._iconQSize, Qt.KeepAspectRatio)
            return scaledIcon


    def rowCount(self, parent = QModelIndex()):

        """ Returns the amount of viewpoints that shall be listed in the view
        """

        return len(self.viewpoints)


    @Slot()
    def resetItems(self, topic = None):

        """ If `topic != None` load viewpoints associated with `topic`, else
        delete the internal state of the model """

        self.beginResetModel()

        if topic is None:
            self.viewpoints = []
        else:
            self.viewpoints = [ vp[1] for vp in pI.getViewpoints(topic, False) ]

        self.endResetModel()


    @Slot()
    def resetView(self):

        """ Reset the view of FreeCAD to the state before the first viewpoint
        was applied """

        pI.resetView()


    @Slot()
    def calcSizes(self):

        """ Convert the millimeter sizes/offsets into pixels depending on the
        current screen. """

        screen = util.getCurrentQScreen()
        # pixels per millimeter (not parts per million)
        ppm = screen.logicalDotsPerInch() / util.MMPI

        width = self._iconSize.width() * ppm
        height = self._iconSize.height() * ppm
        self._iconQSize = QSize(width, height)


    @Slot(QModelIndex)
    def activateViewpoint(self, index):

        """ Manipulates FreeCAD's object viewer according to the setting of the
        viewpoint. """

        if not index.isValid() or index.row() >= len(self.viewpoints):
            return False

        vpRef = self.viewpoints[index.row()]
        camType = None
        if vpRef.viewpoint.oCamera is not None:
            camType = CamType.ORTHOGONAL
        elif vpRef.viewpoint.pCamera is not None:
            camType = CamType.PERSPECTIVE

        result = pI.activateViewpoint(vpRef.viewpoint, camType)
        if result == pI.OperationResults.FAILURE:
            return False
        return True


    def setIconSize(self, size: QSize):

        """ Size is expected to be given in millimeters. """

        self._iconSize = size
        self.calcSizes()


class TopicMetricsModel(QAbstractTableModel):

    """ Model for the table that shows metrics of the topic.

    The uuid will not be visible in the metrics view. """


    def __init__(self, parent = None):

        QAbstractTableModel.__init__(self, parent)
        self.disabledIndices = [ 1, 2, 7, 8 ]
        """ Indices of items that cannot be edited and shall be disabled. """
        self.topic = None
        """ Currently open topic """
        self.members = []
        """ List of all names of members of a topic that shall be displayed.
        """


    def data(self, index, role = Qt.DisplayRole):

        """ Returns the value for a member topic specified by `index`. """

        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        member = self.members[index.row()]
        if index.column() == 0:
            return member.xmlName
        elif index.column() == 1:
            return str(member.value)
        else:
            # I don't know what an additional column could display actually
            return None


    def headerData(self, section, orientation, role = Qt.DisplayRole):

        """ Returns the data that shall be displayed in the horiz. header row.
        """

        header = None
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                header = "Property"
            elif section == 1:
                header = "Value"

        return header


    def flags(self, index):

        """ Items, if not in the disabled list, can be edited and selected. """

        flags = Qt.NoItemFlags
        if not index.isValid():
            return flags
        # every disabled row just shall be greyed out, but its content still
        # visible
        if index.column() == 0:
            flags |= Qt.ItemIsSelectable
            flags |= Qt.ItemIsEnabled

        if index.column() == 1:
            flags = Qt.ItemIsSelectable
            flags |= Qt.ItemIsEditable
            flags |= Qt.ItemIsEnabled

        if index.column() == 1 and index.row() in self.disabledIndices:
            flags = Qt.NoItemFlags

        return flags


    def setData(self, index, value, role = Qt.EditRole):

        """ Update a member of topic with the value entered by the user """

        if not index.isValid():
            return False

        try:
            self.members[index.row()].value = value[0]
        except Exception as err:
            logger.error(str(err))
            return False

        result = pI.modifyElement(self.topic, value[1])
        if result == pI.OperationResults.FAILURE:
            return False

        topic = pI.getTopic(self.topic)
        self.resetItems(topic)
        return True


    def rowCount(self, parent = QModelIndex()):

        """ Returns the number of properties the view shall display.

        There are exactly only 12 members whose values can be displayed in the
        property value tableview. """

        return 12


    def columnCount(self, parent = QModelIndex()):

        """ Returns the number of columns to be displayed in the tableview.

        Only two columns will be shown. The first contains the name of the
        value, the second one the value itself.
        """

        return 2


    @Slot(Topic)
    def resetItems(self, topic = None):

        """ Resets the internal state of the model to the new topic, or its
        initial state. """

        self.beginResetModel()

        if topic is None:
            self.topic = None
            self.members = []
        else:
            self.topic = topic
            self.members = self.createMembersList(self.topic)

        self.endResetModel()


    def createMembersList(self, topic):

        """ Create and return an ordered list of members, in the order they
        shall be shown.

        An object inside this list will be the underlying object representing
        the value. This is done to be able to access the xmlName which is used
        as the name of the value.
        """

        members = [topic._title, topic._date, topic._author, topic._type,
                topic._status, topic._priority, topic._index, topic._modDate,
                topic._modAuthor, topic._dueDate, topic._assignee,
                topic._description ]

        return members


class AdditionalDocumentsModel(QAbstractTableModel):

    """ Model intended to supply a table view with data about the additional
    document references of a topic.

    As with comments, here also the notion of a special reference is
    introduced. A special reference is one whose associated path does exist on
    the local system. It thus is painted in blue. Other references are painted
    in black.
    """

    def __init__(self, parent = None):

        QAbstractTableModel.__init__(self, parent)
        self.topic = None
        self.documents = []


    def rowCount(self, parent = QModelIndex()):

        return len(self.documents)


    def columnCount(self, parent = QModelIndex()):

        return 2 # external, description, reference


    def data(self, index, role = Qt.DisplayRole):

        if not index.isValid():
            return None

        ret_val = None
        if role == Qt.DisplayRole:
            if index.column() == 0:
                ret_val = self.documents[index.row()].description
            elif index.column() == 1:
                ret_val = str(self.documents[index.row()].reference)

        path = self.getFilePath(index)
        isPath = os.path.exists(path)
        if role == Qt.ForegroundRole:
            brush = QApplication.palette().text()
            if index.column() == 0:
                if isPath:
                    brush = QApplication.palette().link()

            ret_val = brush

        return ret_val


    def headerData(self, section, orientation, role = Qt.DisplayRole):

        if role != Qt.DisplayRole:
            return None

        header = None
        if orientation == Qt.Horizontal:
            if section == 0:
                header = "Description"
            elif section == 1:
                header = "Path"

        return header


    @Slot()
    def resetItems(self, topic = None):

        self.beginResetModel()

        if topic is None:
            self.documents = []
            self.topic = None

        else:
            self.createDocumentsList(topic)
            self.topic = topic

        self.endResetModel()


    def createDocumentsList(self, topic):

        self.documents = topic.docRefs


    def getFilePath(self, index):

        global bcfDir

        if not index.isValid():
            return None

        if index.row() >= len(self.documents):
            return None

        doc = self.documents[index.row()]
        path = str(doc.reference)
        if not doc.external:
            sysTmp = util.getBcfDir()
            path = os.path.join(sysTmp, path)

        return path


class RelatedTopicsModel(QAbstractListModel):


    def __init__(self, parent = None):

        QAbstractListModel.__init__(self, parent)
        # holds a list of all topic objects referenced by the "relatedTopics"
        # list inside the current topic object `topic`
        self.relTopics = list()
        self.topic = None


    def flags(self, index):

        """ The resulting list shall only be read only.

        In the future however it is possible to also let the user add related
        topics.
        """

        flgs = Qt.ItemIsEnabled
        flgs |= Qt.ItemIsSelectable

        return flgs


    def rowCount(self, parent = QModelIndex()):

        return len(self.relTopics)


    def data(self, index, role = Qt.DisplayRole):

        if not index.isValid():
            return None

        if index.row() >= len(self.relTopics):
            logger.info("A too large index was passed! Please report the"\
                    " steps you did as issue on the plugin's github page.")
            return None

        if role != Qt.DisplayRole:
            return None

        idx = index.row()
        topicTitle = self.relTopics[idx].title

        return topicTitle


    @Slot()
    def resetItems(self, topic = None):

        self.beginResetModel()

        if topic is None:
            self.relTopics = list()
            self.topic = None

        else:
            self.createRelatedTopicsList(topic)
            self.topic = topic

        self.endResetModel()


    def createRelatedTopicsList(self, topic):

        if topic is None:
            return False

        relatedTopics = topic.relatedTopics
        for t in relatedTopics:
            # in this list only the uid of a topic is stored
            tUId = t.value
            logger.debug("Getting topic to: {}:{}".format(tUId, tUId.__class__))
            match = pI.getTopicFromUUID(tUId)
            if match != pI.OperationResults.FAILURE:
                self.relTopics.append(match)
                logger.debug("Got a match {}".format(match.title))
            else:
                logger.debug("Got nothing back")

