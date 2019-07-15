from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import (QModelIndex, Slot, QSize, QPoint, Signal, Qt, QRect)

from copy import copy
import bcfplugin.util as util


commentRegex = "[a-zA-Z0-9.,\-\/ ]* -- .*@.*"

class CommentDelegate(QStyledItemDelegate):

    invalidInput = Signal((QModelIndex,))

    def __init__(self, parent = None):

        QStyledItemDelegate.__init__(self, parent)
        self.baseFontSize = 12
        self.commentFont = QFont("times")
        self.updateFonts(self.commentFont)

        self.commentYOffset = 10


    def drawComment(self, comment, painter, fontMetric, leftX, topY, brush):

        painter.save()
        pen = painter.pen()
        pen.setColor(brush.color())
        painter.setPen(pen)

        commentTextHeight = fontMetric.height()
        commentTextWidth = fontMetric.width(comment[0])
        commentStart = QPoint(leftX + 10, topY + fontMetric.height())
        painter.drawText(commentStart, comment[0])
        painter.restore()

        return commentStart, commentTextHeight


    def drawSeparationLine(self, painter, pen, start: QPoint, end: QPoint):

        pen.setColor("lightGray")
        painter.setPen(pen)
        painter.drawLine(start, end)
        start = QPoint(start.x(), start.y() + 1)
        end = QPoint(end.x(), end.y() + 1)
        painter.drawLine(start, end)


    def drawAuthorDate(self, comment,
            painter, pen,
            start: QPoint, end: QPoint):

        fontMetric = QFontMetrics(self.authorFont)
        pen.setColor(QColor("#666699"))
        painter.setPen(pen)
        painter.setFont(self.authorFont)
        painter.drawText(start, comment[1])

        dateStart = QPoint(end.x() + 10, end.y())
        painter.drawText(dateStart, comment[2])


    def paint(self, painter, option, index):

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        idx = index.row()

        comment = index.model().data(index, Qt.DisplayRole)
        # top y coordinate at which drawing will begin downwards
        drawingRect = super().initStyleOption(option, index)
        leftX = option.rect.x()
        topY = option.rect.y()

        # save painter state, since color and font are changed
        painter.save()

        # whole area that can be drawn onto
        boundingRect = painter.viewport()

        # extract pen and font from painter
        pen = painter.pen()
        self.updateFonts(painter.font())
        fontMetric = painter.fontMetrics()

        # draw comment
        brush = index.model().data(index, Qt.ForegroundRole)
        (commentStart, commentTextHeight) = self.drawComment(comment,
                painter, fontMetric, leftX, topY, brush)

        # draw separation line
        lineStart = QPoint(commentStart.x(),
                commentStart.y() + commentTextHeight / 2)
        lineEnd = QPoint(lineStart.x() + boundingRect.width() - 20,
                lineStart.y())
        self.drawSeparationLine(painter, pen, lineStart, lineEnd)

        # draw author
        authorStart = QPoint(lineStart.x(),
                lineStart.y() + fontMetric.height())
        authorWidth = fontMetric.width(comment[1])
        authorEnd = QPoint(authorStart.x() + authorWidth,
                authorStart.y())
        self.drawAuthorDate(comment, painter, pen, authorStart,
                authorEnd)

        painter.restore()


    def createEditor(self, parent, option, index):

        """ Makes the comment and the author available in a QLineEdit """

        comment = index.model().data(index, Qt.EditRole)
        startText = comment[0] + " -- " + comment[1]

        validator = QRegExpValidator()
        validator.setRegExp(commentRegex)
        editor = QLineEdit(startText, parent)
        editor.setValidator(validator)
        editor.setFrame(True)

        return editor


    def setEditorData(self, editor, index):

        """ Updates the editor data with the data at `index` in the model """

        comment = index.model().data(index, Qt.EditRole)
        editorText = comment[0] + " -- " + comment[1]
        editor.setText(editorText)


    def setModelData(self, editor, model, index):

        """ Updates the model at `index` with the current text of the editor """

        text = editor.text()
        success = model.setData(index, text)
        if not success:
            util.showError("The comment hast to be separated by '--' from the" \
                    " email address!")
            util.printError("Here we have an invalid string")


    def updateFonts(self, baseFont):

        """ Set the internal fonts to baseFont and update their sizes """

        self.commentFont = copy(baseFont)
        self.commentFont.setBold(True)
        self.commentFont.setPointSize(self.baseFontSize)

        self.authorFont = copy(baseFont)
        self.authorFont.setPointSize(self.baseFontSize - 4)


    def calcCommentSize(self, comment, option):

        """ Calculate the size of a comment element """

        commentFontMetric = QFontMetrics(self.commentFont)
        authorFontMetric = QFontMetrics(self.authorFont)

        commentTextHeight = commentFontMetric.height()
        authorTextHeight = authorFontMetric.height()

        commentWidth = commentFontMetric.width(comment[0])
        authorDateWidth = authorFontMetric.width(comment[1] + comment[2]) + 10
        # +1 is the separation line that is drawn
        # commentTextHeight / 2 is the offset from the comment text towards the
        # separation line
        height = (commentTextHeight + authorTextHeight +
                commentTextHeight / 2 + self.commentYOffset + 1)
        width = commentWidth if commentWidth > authorDateWidth else authorDateWidth

        size = QSize(width, height)
        return size


    def sizeHint(self, option, index):

        """ Return the size of a comment element. """

        comment = index.model().data(index, Qt.DisplayRole)
        size = self.calcCommentSize(comment, option)

        return size
