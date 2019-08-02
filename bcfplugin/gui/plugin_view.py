import sys
if __name__ == "__main__":
    sys.path.append("../../")
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QModelIndex, Slot, Signal,
        QDir, QPoint, QSize)

import bcfplugin.gui.plugin_model as model
import bcfplugin.gui.plugin_delegate as delegate
import bcfplugin.util as util
from bcfplugin.rdwr.viewpoint import Viewpoint


def tr(text):

    """ Placeholder for the Qt translate function. """

    return text


class CommentView(QListView):

    specialCommentSelected = Signal((Viewpoint))

    def __init__(self, parent = None):

        QListView.__init__(self, parent)
        self.setMouseTracking(True)
        self.lastEnteredIndex = None
        self.entered.connect(self.mouseEntered)
        self.delBtn = None


    @Slot()
    def mouseEntered(self, index):

        """ Display a delete button if the mouse hovers over a comment.

        The button is then wired to a dynamically created clicked handler. This
        handler will be passed the index of the hovered over element as
        parameter. """

        if self.delBtn is not None:
            self.deleteDelBtn()

        options = QStyleOptionViewItem()
        options.initFrom(self)

        btnText = "Delete"
        deleteButton = QPushButton(self)
        deleteButton.setText(btnText)
        deleteButton.clicked.connect(lambda: self.deleteElement(index))

        buttonFont = deleteButton.font()
        fontMetric = QFontMetrics(buttonFont)
        btnMinSize = fontMetric.boundingRect(btnText).size()
        deleteButton.setMinimumSize(btnMinSize)

        itemRect = self.rectForIndex(index)
        x = itemRect.width() - deleteButton.geometry().width()
        y = itemRect.y() + (itemRect.height() -
                deleteButton.geometry().height()) / 2
        util.debug("DeleteButton y start: {}".format(y))
        deleteButton.move(x, y)

        deleteButton.show()
        self.delBtn = deleteButton


    def currentChanged(self, current, previous):

        """ If the current comment links to a viewpoint then select that
        viewpoint in viewpointsList.  """

        model = current.model()
        if model is None:
            # no topic is selected, so no comments are loaded
            return

        viewpoint = model.referencedViewpoint(current)
        if viewpoint is not None:
            self.specialCommentSelected.emit(viewpoint)


    def resizeEvent(self, event):

        """ Propagates the new width of the widget to the delegate """

        newSize = self.size()
        self.itemDelegate().setWidth(newSize.width())
        QListView.resizeEvent(self, event)


    @Slot()
    def deleteDelBtn(self):

        """ Delete the comment delete button from the view. """

        if self.delBtn is not None:
            self.delBtn.deleteLater()
            self.delBtn = None


    def deleteElement(self, index):

        """ Handler for deleting a comment when the comment delete button was
        pressed """

        util.debug("Deleting element at index {}".format(index.row()))
        success = index.model().removeRow(index)
        if success:
            self.deleteDelBtn()
        else:
            util.showError("Could not delete comment.")


class SnapshotView(QListView):

    def __init__(self, parent = None):

        QListView.__init__(self, parent)
        self.minIconSize = QSize(100, 100)
        self.doubleClicked.connect(self.openSnapshot)


    def resizeEvent(self, event):

        newSize = self.size()
        rowCount = self.model().rowCount()
        rowCount = rowCount if rowCount > 0 else 1

        newItemWidth = newSize.width() / rowCount
        newItemWidth -= (rowCount - 1) * self.spacing()
        newItemSize = QSize(newItemWidth, newSize.height())

        if (newItemWidth < self.minIconSize.width()):
            newItemSize.setWidth(self.minIconSize.width())
        elif (newItemSize.height() < self.minIconSize.height()):
            newItemSize.setHeight(self.minIconSize.height())

        self.model().setSize(newItemSize)
        self.setIconSize(newItemSize)
        QListView.resizeEvent(self, event)


    @Slot()
    def openSnapshot(self, idx):

        img = self.model().realImage(idx)
        lbl = QLabel(self)
        lbl.setWindowFlags(Qt.Window)
        lbl.setPixmap(img)
        lbl.show()


class ViewpointsListView(QListView):

    def __init__(self, parent = None):

        QListView.__init__(self, parent)


    @Slot(Viewpoint)
    def selectViewpoint(self, viewpoint: Viewpoint):

        util.debug("Hello now I should select an element right?")
        start = self.model().createIndex(0, 0)
        searchValue = str(viewpoint.file) + " (" + str(viewpoint.id) + ")"
        matches = self.model().match(start, Qt.DisplayRole, searchValue)
        if len(matches) > 0:
            util.debug("Is it element: {}".format(matches[0].row()))
            self.setCurrentIndex(matches[0])


    @Slot(QModelIndex, QPushButton)
    def activateViewpoint(self, index, rstBtn):

        result = self.model().activateViewpoint(index)
        if result:
            rstBtn.show()


    def findViewpoint(self, desired: Viewpoint):

        index = -1
        for i in range(0, self.model().rowCount()):
            index = self.model().createIndex(i, 0)
            data = self.model().data(index, Qt.DisplayRole)

            if str(desired.id) in data:
                index = i
                break

        return index


class MyMainWindow(QWidget):

    projectOpened = Signal()

    def __init__(self):
        QWidget.__init__(self, None)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")

        self.projectGroup = self.createProjectGroup()
        self.mainLayout.addWidget(self.projectGroup)

        self.topicGroup = self.createTopicGroup()
        self.topicGroup.hide()
        self.mainLayout.addWidget(self.topicGroup)

        self.commentGroup = self.createCommentGroup()
        self.commentGroup.hide()
        self.mainLayout.addWidget(self.commentGroup)

        # snapshotArea is a stacked widget and will be used for the viewpoint
        # area too
        self.snapshotArea = self.createSnapshotGroup()
        self.snapshotArea.hide()
        self.mainLayout.addWidget(self.snapshotArea)

        # handlers for an opened project
        self.projectOpened.connect(self.topicCbModel.projectOpened)
        self.projectOpened.connect(self.openedProjectUiHandler)
        # reset models for every opened project
        self.projectOpened.connect(self.commentModel.resetItems)
        self.projectOpened.connect(self.commentList.deleteDelBtn)
        self.projectOpened.connect(self.snapshotModel.resetItems)
        self.projectOpened.connect(self.viewpointsModel.resetItems)
        self.projectOpened.connect(self.relTopModel.resetItems)
        # reset both the combobox and the stacked widget beneath to the first
        # index for an opened project
        self.projectOpened.connect(lambda: self.snStack.setCurrentIndex(0))
        self.projectOpened.connect(lambda: self.snStackSwitcher.setCurrentIndex(0))
        # create editor for a double left click on a comment
        self.commentList.doubleClicked.connect(
                lambda idx: self.commentList.edit(idx))
        # reset ui after a topic switch, to not display any artifacts from the
        # previous topic
        self.topicCbModel.selectionChanged.connect(self.commentModel.resetItems)
        self.topicCbModel.selectionChanged.connect(self.commentList.deleteDelBtn)
        self.topicCbModel.selectionChanged.connect(self.snapshotModel.resetItems)
        self.topicCbModel.selectionChanged.connect(self.viewpointsModel.resetItems)
        self.topicCbModel.selectionChanged.connect(self.topicDetailsBtn.show)
        self.topicCbModel.selectionChanged.connect(self.topicDetailsModel.resetItems)
        self.topicCbModel.selectionChanged.connect(self.addDocumentsModel.resetItems)
        self.topicCbModel.selectionChanged.connect(self.relTopModel.resetItems)
        # reset both the combobox and the stacked widget beneath to the first
        # index for a topic switch
        self.topicCbModel.selectionChanged.connect(lambda: self.snStack.setCurrentIndex(0))
        self.topicCbModel.selectionChanged.connect(lambda: self.snStackSwitcher.setCurrentIndex(0))
        # connect the stacked widget with the combobox
        self.snStackSwitcher.activated.connect(self.snStack.setCurrentIndex)
        # select a viewpoint if a referncing comment is selected
        self.commentList.specialCommentSelected.connect(lambda x:
                self.snStack.setCurrentIndex(1))
        self.commentList.specialCommentSelected.connect(lambda x:
                self.snStackSwitcher.setCurrentIndex(1))
        self.commentList.specialCommentSelected.connect(self.viewpointList.selectViewpoint)
        # open the topic metrics window
        self.topicDetailsBtn.pressed.connect(self.showTopicMetrics)
        # activate a viewpoint using viewController.py
        self.viewpointList.doubleClicked.connect(lambda x:
                self.viewpointList.activateViewpoint(x, self.viewpointResetBtn))
        self.viewpointResetBtn.clicked.connect(self.viewpointsModel.resetView)
        self.viewpointResetBtn.clicked.connect(self.viewpointResetBtn.hide)

        self.setLayout(self.mainLayout)

        self.openFilePath = ""


    def createProjectGroup(self):

        projectGroup = QGroupBox()
        projectGroup.setObjectName("projectGroup")

        self.projectLayout = QHBoxLayout(projectGroup)
        self.projectLayout.setObjectName("projectLayout")

        self.projectLabel = QLabel("Open Project")
        self.projectLabel.setObjectName("projectLabel")
        self.projectLayout.addWidget(self.projectLabel)

        self.projectSaveButton = QPushButton("Save")
        self.projectSaveButton.setObjectName("projectSaveButton")
        self.projectSaveButton.clicked.connect(self.saveProjectHandler)
        self.projectSaveButton.hide()

        self.projectButton = QPushButton("Open")
        self.projectButton.setObjectName("projectButton")
        self.projectButton.clicked.connect(self.openProjectBtnHandler)
        self.projectButton.clicked.connect(self.projectSaveButton.show)

        self.projectLayout.addWidget(self.projectButton)
        self.projectLayout.addWidget(self.projectSaveButton)

        return projectGroup


    def createTopicGroup(self):

        topicGroup = QGroupBox()
        topicGroup.setObjectName("topicGroup")

        self.topicLabel = QLabel("Topic: ")

        self.topicCb = QComboBox()
        self.topicCbModel = model.TopicCBModel()
        self.topicCb.setModel(self.topicCbModel)
        self.topicCb.currentIndexChanged.connect(self.topicCbModel.newSelection)

        self.topicDetailsBtn = QPushButton("Details")
        self.topicDetailsBtn.hide()

        # setup models for topic details window
        self.topicDetailsModel = model.TopicMetricsModel()
        self.topicDetailsDelegate = delegate.TopicMetricsDelegate()
        self.addDocumentsModel = model.AdditionalDocumentsModel()
        self.relTopModel = model.RelatedTopicsModel()

        self.topicHLayout = QHBoxLayout(topicGroup)
        self.topicHLayout.addWidget(self.topicLabel)
        self.topicHLayout.addWidget(self.topicCb)
        self.topicHLayout.addWidget(self.topicDetailsBtn)

        return topicGroup


    def createCommentGroup(self):

        commentGroup = QGroupBox()
        commentGroup.setObjectName("commentGroup")

        self.commentLayout = QVBoxLayout(commentGroup)
        self.commentList = CommentView()

        self.commentModel = model.CommentModel()
        self.commentList.setModel(self.commentModel)

        self.commentDelegate = delegate.CommentDelegate()
        self.commentList.setItemDelegate(self.commentDelegate)

        self.commentLayout.addWidget(self.commentList)

        self.commentPlaceholder = "Enter a new comment here"
        self.commentValidator = QRegExpValidator()
        self.commentValidator.setRegExp(delegate.commentRegex)
        self.newCommentEdit = QLineEdit()
        self.newCommentEdit.returnPressed.connect(self.checkAndAddComment)
        self.newCommentEdit.setPlaceholderText(self.commentPlaceholder)
        self.commentLayout.addWidget(self.newCommentEdit)

        return commentGroup


    def createSnapshotGroup(self):

        snGroup = QGroupBox()
        self.snGroupLayout = QVBoxLayout(snGroup)

        self.snapshotModel = model.SnapshotModel()
        self.snapshotList = SnapshotView()
        self.snapshotList.setModel(self.snapshotModel)

        self.viewpointsModel = model.ViewpointsListModel(self.snapshotModel)
        self.viewpointList = ViewpointsListView()
        self.viewpointList.setModel(self.viewpointsModel)

        self.snStack = QStackedWidget()
        self.snStack.addWidget(self.snapshotList)
        self.snStack.addWidget(self.viewpointList)

        self.viewpointResetBtn = QPushButton("Reset View")
        self.viewpointResetBtn.hide()

        self.snStackSwitcher = QComboBox()
        self.snStackSwitcher.addItem(tr("Snapshot Bar"))
        self.snStackSwitcher.addItem(tr("Viewpoint List"))

        self.snGroupLayout.addWidget(self.snStackSwitcher)
        self.snGroupLayout.addWidget(self.snStack)
        self.snGroupLayout.addWidget(self.viewpointResetBtn)

        return snGroup


    @Slot()
    def openedProjectUiHandler(self):

        print("setting up view")

        self.projectLabel.setText(model.getProjectName())
        self.projectButton.setText("Open other")
        self.topicGroup.show()
        self.commentGroup.show()
        self.snapshotArea.show()


    @Slot()
    def openProjectBtnHandler(self):

        lastPath = self.openFilePath
        dflPath = lastPath if lastPath != "" else QDir.homePath()

        filename = QFileDialog.getOpenFileName(self, self.tr("Open BCF File"),
                dflPath,  self.tr("BCF Files (*.bcf *.bcfzip)"))
        if filename[0] != "":
            model.openProjectBtnHandler(filename[0])
            self.openFilePath = filename[0]
            self.projectOpened.emit()


    @Slot()
    def checkAndAddComment(self):

        util.debug("Pressed enter on the input")
        editor = self.newCommentEdit
        text = editor.text()

        if util.isAuthorSet():
            modAuthor = util.getAuthor()
        else:
            delegate.openAuthorsDialog(None)

        self.addComment()


    @Slot()
    def addComment(self):

        text = self.newCommentEdit.text()
        success = self.commentModel.addComment((text, util.getAuthor()))
        if not success:
            util.showError("Could not add a new comment")
            return

        # delete comment on successful addition
        self.newCommentEdit.setText("")


    @Slot()
    def saveProjectHandler(self):

        dflPath = self.openFilePath
        filename = QFileDialog.getSaveFileName(self, self.tr("Save BCF File"),
                dflPath,  self.tr("BCF Files (*.bcf *.bcfzip)"))
        if filename != "":
            util.debug("Got a file to write to: {}.".format(filename))
            model.saveProject(filename[0])


    @Slot()
    def showTopicMetrics(self):

        metricsWindow = QDialog(self)

        layout = QVBoxLayout()
        metricsWindow.setLayout(layout)

        topicMetrics = QTableView()
        topicMetrics.setModel(self.topicDetailsModel)
        topicMetrics.setItemDelegate(self.topicDetailsDelegate)
        layout.addWidget(topicMetrics)

        addDocGroup = QGroupBox()
        addDocGroup.setTitle("Additional Documents")
        addDocGroupLayout = QVBoxLayout(addDocGroup)
        addDocTable = QTableView()
        addDocTable.setModel(self.addDocumentsModel)
        addDocGroupLayout.addWidget(addDocTable)
        layout.addWidget(addDocGroup)

        relTopGroup = QGroupBox()
        relTopGroup.setTitle("Related Topics")
        relTopGroupLayout = QVBoxLayout(relTopGroup)
        relTopList = QListView()
        relTopList.setModel(self.relTopModel)
        relTopGroupLayout.addWidget(relTopList)
        layout.addWidget(relTopGroup)

        metricsWindow.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    plugin = MyMainWindow()
    plugin.show()

    app.exec_()
    sys.exit()
