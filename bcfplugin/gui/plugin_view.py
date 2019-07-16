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


class CommentView(QListView):

    def __init__(self, parent = None):

        QListView.__init__(self, parent)
        self.setMouseTracking(True)
        self.lastEnteredIndex = None
        self.entered.connect(self.mouseEntered)
        self.delBtn = None


    @Slot()
    def mouseEntered(self, index):

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
        minWidth = fontMetric.width(btnText)
        minHeight = fontMetric.height()
        btnMinSize = QSize(minWidth, minHeight)
        deleteButton.setMinimumSize(btnMinSize)

        itemRect = self.rectForIndex(index)
        x = itemRect.width() - deleteButton.geometry().width()
        y = itemRect.y() + (itemRect.height() -
                deleteButton.geometry().height()) / 2
        deleteButton.move(x, y)

        deleteButton.show()
        self.delBtn = deleteButton


    def deleteDelBtn(self):

        self.delBtn.deleteLater()
        self.delBtn = None


    def deleteElement(self, index):

        util.debug("Deleting element at index {}".format(index.row()))
        success = index.model().removeRow(index)
        if success:
            self.deleteDelBtn()
        else:
            util.showError("Could not delete comment.")


    def resizeEvent(self, event):

        """ Propagates the new width of the widget to the delegate """

        newSize = self.size()
        self.itemDelegate().setWidth(newSize.width())
        QListView.resizeEvent(self, event)


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

        self.projectOpened.connect(self.topicCbModel.projectOpened)
        self.projectOpened.connect(self.openedProjectUiHandler)
        self.projectOpened.connect(self.commentModel.resetItems)
        self.commentList.doubleClicked.connect(
                lambda idx: self.commentList.edit(idx))
        self.topicCbModel.selectionChanged.connect(self.commentModel.resetItems)
        self.topicCbModel.selectionChanged.connect(self.snapshotModel.resetItems)

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

        self.topicHLayout = QHBoxLayout(topicGroup)
        self.topicHLayout.addWidget(self.topicLabel)
        self.topicHLayout.addWidget(self.topicCb)

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
        self.commentDelegate.invalidInput.connect(self.commentList.edit)


        self.commentLayout.addWidget(self.commentList)

        self.commentPlaceholder = "comment -- author email"
        self.commentValidator = QRegExpValidator()
        self.commentValidator.setRegExp(delegate.commentRegex)
        self.newCommentEdit = QLineEdit()
        self.newCommentEdit.returnPressed.connect(self.checkAndAddComment)
        self.newCommentEdit.setPlaceholderText(self.commentPlaceholder)
        self.commentLayout.addWidget(self.newCommentEdit)

        return commentGroup


    def createSnapshotGroup(self):

        snStack = QStackedWidget()

        self.snapshotModel = model.SnapshotModel()
        self.snapshotList = SnapshotView()
        self.snapshotList.setModel(self.snapshotModel)

        snStack.addWidget(self.snapshotList)
        return snStack


    def createViewpointGroup(self):
        #TODO: implement
        pass


    @Slot()
    def openedProjectUiHandler(self):

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
        if self.commentValidator.validate(text, 0) == QValidator.Invalid:
            QToolTip.showText(editor.mapToGlobal(QPoint()), "Invalid Input."\
                    " Template for a comment is: <comment text> -- <email address>")
            return
        self.addComment()


    @Slot()
    def addComment(self):

        text = self.newCommentEdit.text()
        success = self.commentModel.addComment(text)
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



if __name__ == "__main__":
    app = QApplication(sys.argv)

    plugin = MyMainWindow()
    plugin.show()

    app.exec_()
    sys.exit()
