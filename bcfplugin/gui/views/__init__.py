
from PySide2.QtWidgets import QLabel
from PySide2.QtCore import QTimer


def createNotificationLabel():

    """ Creates a label intended to show raw text notifications. """

    lbl = QLabel()
    lbl.hide()

    return lbl


def showNotification(self, text):

    """ Shows a notification with content `text` in `notificationLabel` of
    `self`.

    The label is shown for 2 1/2 seconds and then it is hidden again.
    """

    self.notificationLabel.setText(text)
    self.notificationLabel.show()
    if (not hasattr(self, "notificationTimer") and
            self.notificationLabel is not None):
        self.notificationTimer = QTimer()
        self.notificationTimer.timeout.connect(lambda:
                self.notificationLabel.hide())
    self.notificationTimer.start(2500)

__all__ = ["createNotificationLabel", "showNotification", "openAuthorsDialog",
        "TopicMetricsDialog", "TopicAddDialog", "ProjectCreateDialog",
        "CommentView", "SnapshotView", "ViewpointsView"]

from bcfplugin.gui.views.authorsdialog import openAuthorsDialog
from bcfplugin.gui.views.topicadddialog import TopicAddDialog
from bcfplugin.gui.views.projectcreatedialog import ProjectCreateDialog
from bcfplugin.gui.views.commentlist import CommentView
from bcfplugin.gui.views.snapshotlist import SnapshotView
from bcfplugin.gui.views.viewpointslist import ViewpointsView
from bcfplugin.gui.views.topicmetricsdialog import TopicMetricsDialog
