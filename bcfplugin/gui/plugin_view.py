import os
import sys
import logging
import platform
import pyperclip
import subprocess
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QAbstractListModel, QModelIndex, Slot, Signal,
        QDir, QPoint, QSize, QTimer)

import bcfplugin
import bcfplugin.util as util
import bcfplugin.gui.models as model
from bcfplugin.gui.models import *
from bcfplugin.gui.views import *
from bcfplugin.gui.delegates import *


logger = bcfplugin.createLogger(__name__)


OBJECTNAME = "bcfplugin"
""" Name of the main window of the plugin. """


def tr(self, text):

    """ Placeholder for the Qt translate function. """

    return self.tr(text)


class MyMainWindow(QWidget):

    """ ... well this is the main window.

    The UI consists of roughly three big sections:
        - the Project/Topic section containing controls to operate on a project
          and topic respectively
        - the comment section: showing a list of comments and a QLineEdit to add
          new comments.
        - the snapshot section: composed of a stacked widget and a combobox to
          switch between the widgets in the stack. The first widget shows a
          horizontal list of snapshots specified in the topic, the second widget
          shows a vertical list of all viewpoints specified in the topic.
    These sections are added to a QSplitter to allow the user to easily resize
    them at will.

    From the main window two form dialogs can be opened. The first one for
    creating a new project. The second one creates a new topic in a new project.

    Two data windows can also be opened: one showing information about a
    particular topic (the topic metrics window) and the other one displaying a
    snapshot in its original resolution.

    Also for a more event driven approach the signal `projectOpened` is defined.
    It gets emitted when a project was opened.
    """

    projectOpened = Signal()
    """ Signal emitted when a BCF file (e.g. project) was opened """

    def __init__(self):

        QWidget.__init__(self, None)

        self.openFilePath = ""
        """ Path to the file that was opened last. """

        self.setObjectName(OBJECTNAME)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.setWindowTitle("BCF-Plugin")

        self.mainSplitter = self.setupSplitter()
        self.mainLayout.addWidget(self.mainSplitter)

        # setup/add of the project/topic section
        self.projectGroup = self.createProjectTopicSection()
        self.mainSplitter.addWidget(self.projectGroup)

        # setup/add of the comment section, initially hidden
        self.commentSection = self.createCommentSection()
        self.commentSection.hide()
        self.mainSplitter.addWidget(self.commentSection)

        # setup/add of the snapshot section, initially hidden
        self.snapshotArea = self.createSnapshotSection()
        self.snapshotArea.hide()
        self.mainSplitter.addWidget(self.snapshotArea)

        # create and add a notification label for the main window
        # it is shown at the bottom of the plugin
        self.notificationLabel = createNotificationLabel()
        self.mainLayout.addWidget(self.notificationLabel)

        """ Handlers for buttons associated with a topic """
        # open a project when the "Open" button was clicked
        self.projectOpenButton.clicked.connect(self.openProjectBtnHandler)
        # after a project is opened, a project cannot be created anymore.
        self.projectOpenButton.clicked.connect(self.projectCreateButton.hide)
        self.projectSaveButton.clicked.connect(self.saveProjectHandler)
        self.projectCreateButton.clicked.connect(self.showCreateProjectDialog)

        """ handlers for an opened project """
        # reset to the original UI state for every opened project
        self.projectOpened.connect(self.projectSaveButton.show)
        self.projectOpened.connect(self.openedProjectUiHandler)
        self.projectOpened.connect(lambda: self.topicListModel.updateTopics())
        self.projectOpened.connect(self.commentList.deleteDelBtn)
        self.projectOpened.connect(self.topicNameLbl.hide)
        # reset the models
        self.projectOpened.connect(self.commentModel.resetItems)
        self.projectOpened.connect(self.snapshotModel.resetItems)
        self.projectOpened.connect(self.viewpointsModel.resetItems)
        self.projectOpened.connect(self.relTopModel.resetItems)
        # reset both the combobox and the stacked widget
        self.projectOpened.connect(lambda: self.snStack.setCurrentIndex(0))
        self.projectOpened.connect(lambda: self.snStackSwitcher.setCurrentIndex(0))
        self.projectOpened.connect(self.hideCommentSnapshotSection)

        """ handlers for a newly selected topic """
        # show the two lower sections
        self.topicListModel.selectionChanged.connect(lambda x:
                self.showCommentSnapshotSection())
        self.topicListModel.selectionChanged.connect(lambda x:
                self.newCommentEdit.setDisabled(False))
        # remove any artifacts from the previous topic
        self.topicListModel.selectionChanged.connect(self.commentList.deleteDelBtn)
        self.topicListModel.selectionChanged.connect(lambda topic:
                self.topicNameLbl.setText(topic.title))
        self.topicListModel.selectionChanged.connect(lambda: self.snStack.setCurrentIndex(0))
        self.topicListModel.selectionChanged.connect(lambda: self.snStackSwitcher.setCurrentIndex(0))
        # set up UI to accommodate new topic
        self.topicListModel.selectionChanged.connect(self.topicDetailsBtn.show)
        self.topicListModel.selectionChanged.connect(self.showCommentSnapshotSection)
        self.topicListModel.selectionChanged.connect(lambda x:
                self.topicNameLbl.show())
        # tell the models about the new topic
        self.topicListModel.selectionChanged.connect(self.commentModel.resetItems)
        self.topicListModel.selectionChanged.connect(self.snapshotModel.resetItems)
        self.topicListModel.selectionChanged.connect(self.viewpointsModel.resetItems)
        self.topicListModel.selectionChanged.connect(self.topicDetailsModel.resetItems)
        self.topicListModel.selectionChanged.connect(self.addDocumentsModel.resetItems)
        self.topicListModel.selectionChanged.connect(self.relTopModel.resetItems)

        """ Handlers for other UI actions """
        # link combobox and stack widget
        self.snStackSwitcher.activated.connect(self.snStack.setCurrentIndex)
        # autoselect viewpoint for selected special comment
        self.commentList.specialCommentSelected.connect(lambda x:
                self.snStack.setCurrentIndex(1))
        self.commentList.specialCommentSelected.connect(lambda x:
                self.snStackSwitcher.setCurrentIndex(1))
        self.commentList.specialCommentSelected.connect(self.viewpointList.selectViewpoint)
        self.topicDetailsBtn.pressed.connect(self.showTopicMetrics)
        self.topicAddBtn.pressed.connect(self.showAddTopicForm)
        # activate a viewpoint using viewController.py
        self.viewpointList.doubleClicked.connect(lambda x:
                self.viewpointList.activateViewpoint(x, self.viewpointResetBtn))
        self.viewpointResetBtn.clicked.connect(self.viewpointsModel.resetView)
        self.viewpointResetBtn.clicked.connect(self.viewpointResetBtn.hide)
        # delete delete button if the view is scrolled
        self.commentList.verticalScrollBar().valueChanged.connect(lambda x:
                self.commentList.deleteDelBtn())

        self.setLayout(self.mainLayout)


    def setupSplitter(self):

        """ Creates a QSplitter element with orientation set to vertical. """

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        return splitter

    """
    The following three create*() functions:
        - createProjectTopicSection
        - createCommentSection
        - createSnapshotSection
    all create a QFrame containing the UI elements comprising the respective
    section. No signals are connected to any sinks here. This is reserved for
    the init funcion to collect the connections all in one place.
    """

    def createProjectTopicSection(self):

        """ Creates a QFrame containing elements comprising the topic and
        project section.

        The margins of the layouts, that share an edge with the plugin, are set
        to 0 to move the elements to the right and left edge respectively."""

        topFrame = QFrame()
        topLayout = QHBoxLayout(topFrame)
        topLayout.setSpacing(0)
        topMargins = topLayout.contentsMargins()
        topMargins.setBottom(0)
        topMargins.setLeft(0)
        topMargins.setRight(0)
        topLayout.setContentsMargins(topMargins)

        projFrame = QFrame()
        projLayout = QVBoxLayout(projFrame)
        projMargins = projLayout.contentsMargins()
        projMargins.setLeft(0)
        projMargins.setBottom(0)
        projLayout.setContentsMargins(projMargins)
        topLayout.addWidget(projFrame)

        self.projectSaveButton = QPushButton(self.tr("Save"))
        self.projectSaveButton.setObjectName("projectSaveButton")
        self.projectSaveButton.hide()

        self.projectOpenButton = QPushButton(self.tr("Open"))
        self.projectOpenButton.setObjectName("projectOpenButton")

        self.projectCreateButton = QPushButton(self.tr("Create"))
        self.projectCreateButton.setObjectName("projectCreateButton")

        projLayout.addWidget(self.projectOpenButton)
        projLayout.addWidget(self.projectCreateButton)
        projLayout.addWidget(self.projectSaveButton)
        projLayout.addStretch(20)

        topicFrame = QFrame()
        topicLayout = QVBoxLayout(topicFrame)
        topicMargins = topicLayout.contentsMargins()
        topicMargins.setRight(0)
        topicMargins.setBottom(0)
        topicLayout.setContentsMargins(topicMargins)
        topLayout.addWidget(topicFrame)

        self.topicAddBtn = QPushButton(self.tr("Add Topic"))
        self.topicAddBtn.setObjectName("addTopicBtn")
        self.topicAddBtn.hide()

        self.topicDetailsBtn = QPushButton(self.tr("Details"))
        self.topicDetailsBtn.setObjectName("topicDetailsBtn")
        self.topicDetailsBtn.hide()

        topicBtnLayout = QHBoxLayout()
        topicBtnLayout.addWidget(self.topicAddBtn)
        topicBtnLayout.addWidget(self.topicDetailsBtn)

        self.topicNameLbl = QLabel()

        self.topicList = QListView()
        self.topicListModel = model.TopicListModel()
        self.topicList.setModel(self.topicListModel)
        self.topicList.setObjectName("topicList")
        self.topicList.doubleClicked.connect(self.topicListModel.newSelection)
        logger.debug("Connected double click signal to newSelection slot")
        self.topicList.hide()

        topicLayout.addWidget(self.topicNameLbl)
        topicLayout.addLayout(topicBtnLayout)
        topicLayout.addWidget(self.topicList)

        # setup models for topic details window
        self.topicDetailsModel = model.TopicMetricsModel()
        self.topicDetailsDelegate = TopicMetricsDelegate()
        self.addDocumentsModel = model.AdditionalDocumentsModel()
        self.relTopModel = model.RelatedTopicsModel()

        return topFrame


    def createCommentSection(self):

        """ Creates a QFrame containing only the comment list and the new
        comment line edit. """

        commentSection = QFrame()
        commentSection.setObjectName("commentSection")

        self.commentLayout = QVBoxLayout(commentSection)
        self.commentLayout.setSpacing(3)
        self.commentLayout.setMargin(0)
        self.commentList = CommentView()

        self.commentModel = model.CommentModel()
        self.commentList.setModel(self.commentModel)

        self.commentDelegate = CommentDelegate()
        self.commentList.setItemDelegate(self.commentDelegate)

        self.commentLayout.addWidget(self.commentList)

        self.commentPlaceholder = self.tr("Enter a new comment here")
        self.newCommentEdit = QLineEdit()
        self.newCommentEdit.returnPressed.connect(self.checkAndAddComment)
        self.newCommentEdit.setPlaceholderText(self.commentPlaceholder)
        self.newCommentEdit.setDisabled(True)

        self.commentLayout.addWidget(self.newCommentEdit)

        return commentSection


    def createSnapshotSection(self):

        """ Creates the snapshot section consisting of a combobox and a stacked
        widget.

        The stacked widget contains itself two widgets:
            - The snapshot list: horizontal list showing at most three
              scaled versions snapshots
            - The viewpoints list: a (normal) vertical list showing viewpoints
              contained in the current topic.
        The combobox is used to switch between these two widgets.
        """

        snGroup = QFrame()
        self.snGroupLayout = QVBoxLayout(snGroup)
        self.snGroupLayout.setSpacing(3)
        self.snGroupLayout.setMargin(0)

        self.snapshotModel = model.SnapshotModel()
        self.snapshotList = SnapshotView()
        self.snapshotList.setModel(self.snapshotModel)

        self.viewpointsModel = model.ViewpointsListModel(self.snapshotModel)
        self.viewpointList = ViewpointsView()
        self.viewpointList.setModel(self.viewpointsModel)

        self.snStack = QStackedWidget()
        self.snStack.addWidget(self.snapshotList)
        self.snStack.addWidget(self.viewpointList)

        self.viewpointResetBtn = QPushButton(self.tr("Reset View"))
        self.viewpointResetBtn.hide()

        self.snStackSwitcher = QComboBox()
        self.snStackSwitcher.addItem(self.tr("Snapshot Bar"))
        self.snStackSwitcher.addItem(self.tr("Viewpoint List"))

        self.snGroupLayout.addWidget(self.snStackSwitcher)
        self.snGroupLayout.addWidget(self.snStack)
        self.snGroupLayout.addWidget(self.viewpointResetBtn)

        return snGroup


    @Slot()
    def openedProjectUiHandler(self):

        """ Handler invoked when the "Open" button is pressed.

        It only does some UI configurations.
        """

        logger.info("setting up view")

        self.projectOpenButton.setText(self.tr("Open other"))
        self.topicList.show()
        self.topicAddBtn.show()


    @Slot()
    def hideCommentSnapshotSection(self):

        """ Hide the comment and snapshot section. """

        self.commentSection.hide()
        self.snapshotArea.hide()


    @Slot()
    def showCommentSnapshotSection(self):

        """ Show the comment and snapshot section. """

        self.commentSection.show()
        self.snapshotArea.show()


    @Slot()
    def openProjectBtnHandler(self):

        """ Handler invoked when the "Open" button is pressed.

        It causes the plugin to open a file open dialog and then subsequently
        opening the, by the user, selected file.
        """

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

        """ Handler invoked when the editing of a new comment is finished.

        It checks whether already an author was set during the lifetime of the
        plugin. If not the authors-dialog will be opened.
        The model associated with the comment list will be called to add the
        new comment with the set author's email address (`modAuthor`)"""

        editor = self.newCommentEdit
        text = editor.text()

        if not util.isAuthorSet():
            openAuthorsDialog(None)
        modAuthor = util.getAuthor()

        success = self.commentModel.addComment((text, modAuthor))
        if not success:
            util.showError(self.tr("Could not add a new comment"))
            return

        # reset line edit
        self.newCommentEdit.setText("")


    @Slot()
    def saveProjectHandler(self):

        """ Handler invoked when the "Save" button was pressed.

        Opens a save file dialog and starts the saving of the current state of
        the project.
        """

        dflPath = self.openFilePath
        filename = QFileDialog.getSaveFileName(self, self.tr("Save BCF File"),
                dflPath,  self.tr("BCF Files (*.bcf *.bcfzip)"))
        if filename[0] != "":
            logger.debug("Got a file to write to: {}.".format(filename))
            model.saveProject(filename[0])


    @Slot()
    def showTopicMetrics(self):

        """ Shows the topic metrics dialog.

        While the dialog is active, the main window of the UI cannot be used.
        """

        metricsWindow = TopicMetricsDialog(self)
        metricsWindow.exec()


    @Slot()
    def showAddTopicForm(self):

        """ Shows the form gathering necessary info to add a new topic to the
        project.

        During the time this window is open the main window is inactive.
        """

        addTopicForm = TopicAddDialog(self)
        addTopicForm.exec()
        self.topicListModel.updateTopics()


    def closeEvent(self, event):

        """ Overrides QWidget's closeEvent function.

        If the project's state state contains unsaved modifications the user is
        asked whether to save the project or not.
        """

        if util.getDirtyBit():
            self.showExitSaveDialog()

        logger.debug("Deleting temporary directory {}".format(util.getSystemTmp()))
        util.deleteTmp()


    def showExitSaveDialog(self):

        """ Shows the dialog asking the user whether or not to save.

        While this dialog is active the main window is inactive. """

        dialog = QDialog(self)
        buttons = QDialogButtonBox(QDialogButtonBox.Save |
                QDialogButtonBox.Close, dialog)
        label = QLabel(self.tr("Save before closing?"))

        layout = QVBoxLayout(dialog)
        layout.addWidget(label)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        buttons.accepted.connect(lambda: self.closeSaveProject(dialog))
        buttons.rejected.connect(lambda: dialog.done(0))
        dialog.exec()


    def closeSaveProject(self, dialog):

        """ Handler invoked when the Close-Dialog's save button is pressed. """

        self.saveProjectHandler()
        dialog.done(0)


    def showCreateProjectDialog(self):

        """ Show the dialog for creating a new project.

        Following the `projectOpened` signal is emitted, to let the plugin
        build up the UI accordingly.
        """

        dialog = ProjectCreateDialog(self)
        dialog.exec()

        self.projectOpened.emit()
