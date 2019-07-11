import sys
if __name__ == "__main__":
    sys.path.append("../../")
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QAbstractListModel, QModelIndex, Slot, QDir, QPoint

import bcfplugin.gui.plugin_model as model
import bcfplugin.gui.plugin_delegate as delegate
import bcfplugin.util as util


class MyMainWindow(QWidget):

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

        self.setLayout(self.mainLayout)


    def createProjectGroup(self):

        projectGroup = QGroupBox()
        projectGroup.setObjectName("projectGroup")

        self.projectLayout = QHBoxLayout(projectGroup)
        self.projectLayout.setObjectName("projectLayout")

        self.projectLabel = QLabel("Open Project")
        self.projectLabel.setObjectName("projectLabel")
        self.projectLayout.addWidget(self.projectLabel)

        self.projectButton = QPushButton("Open")
        self.projectButton.setObjectName("projectButton")
        self.projectButton.clicked.connect(self.openProjectBtnHandler)
        self.projectLayout.addWidget(self.projectButton)

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
        self.commentList = QListView()

        self.commentModel = model.CommentModel()
        self.commentList.setModel(self.commentModel)

        self.commentDelegate = delegate.CommentDelegate()
        self.commentList.setItemDelegate(self.commentDelegate)
        self.commentDelegate.invalidInput.connect(self.commentList.edit)

        self.commentList.doubleClicked.connect(
                lambda idx: self.commentList.edit(idx))
        self.topicCbModel.selectionChanged.connect(self.commentModel.resetItems)

        self.commentLayout.addWidget(self.commentList)

        self.commentPlaceholder = "comment -- author email"
        self.newCommentEdit = QLineEdit()
        self.newCommentEdit.returnPressed.connect(self.checkAndAddComment)
        self.commentValidator = QRegExpValidator()
        self.commentValidator.setRegExp(delegate.commentRegex)
        #self.newCommentEdit.setValidator(validator)
        self.newCommentEdit.setPlaceholderText(self.commentPlaceholder)
        self.commentLayout.addWidget(self.newCommentEdit)

        return commentGroup


    def createViewpointGroup(self):
        #TODO: implement
        pass


    @Slot()
    def openProjectBtnHandler(self):

        dflPath = QDir.homePath()
        filename = QFileDialog.getOpenFileName(self, self.tr("Open BCF File"),
                dflPath,  self.tr("BCF Files (*.bcf *.bcfzip)"))
        if filename[0] != "":
            model.openProjectBtnHandler(filename[0])
            self.projectLabel.setText(model.getProjectName())
            self.projectButton.setText("Open other")
            self.topicCbModel.projectOpened()
            self.topicGroup.show()
            self.commentGroup.show()


    @Slot()
    def checkAndAddComment(self):

        util.debug("Pressed enter on the input")
        editor = self.newCommentEdit
        text = editor.text()
        if not self.commentValidator.validate(text, 0) == QValidator.Acceptable:
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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    plugin = MyMainWindow()
    plugin.show()

    app.exec_()
    sys.exit()
