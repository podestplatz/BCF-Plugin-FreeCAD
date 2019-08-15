"""
Copyright (C) 2019 PODEST Patrick

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

from PySide2.QtWidgets import QLabel
from PySide2.QtCore import QTimer


def createNotificationLabel():

    """ Creates a label intended to show raw text notifications. """

    lbl = QLabel()
    lbl.hide()

    return lbl


def hideNotificationHandler(self):

    """ Handler for the notification timer hiding the label again. """

    if self.notificationLabel is not None:
        self.notificationLabel.hide()


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
        self.notificationTimer.setSingleShot(True)
        self.notificationTimer.timeout.connect(lambda:
                hideNotificationHandler(self))
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
