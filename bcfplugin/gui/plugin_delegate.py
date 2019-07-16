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
        self.widgetWidth = 0
        self.verticalOffset = -1

        self.commentYOffset = 10


    def drawComment(self, comment, painter, option, fontMetric, leftX, topY, brush):

        painter.save()
        pen = painter.pen()
        pen.setColor(brush.color())
        painter.setPen(pen)

        commentBoundRect = self.getCommentRect(comment, option)
        commentBoundRect.setX(leftX + 10)
        commentBoundRect.setY(commentBoundRect.y() + self.commentYOffset)

        painter.drawText(commentBoundRect,
                Qt.TextWordWrap | Qt.AlignLeft,
                comment[0])
        painter.restore()

        return commentBoundRect.bottomLeft(), commentBoundRect.height()


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


    def setVerticalOffset(self, paintDevice):

        """ Set the vertical offset to one milimeter, using paintDevice to get DPI
        in the y direction. """

        offset = (paintDevice.logicalDpiY() / 25.4) * 1
        self.verticalOffset = offset


    def paint(self, painter, option, index):

        if option.state & QStyle.State_Selected:
            painter.fillRect(styleOption.rect, option.palette.highlight())
        idx = index.row()

        if self.verticalOffset == -1:
            self.setVerticalOffset(painter.device())

        comment = index.model().data(index, Qt.DisplayRole)
        # top y coordinate at which drawing will begin downwards
        drawingOption = super().initStyleOption(option, index)
        #drawingRect = drawingOption.rect
        #TODO switch to drawingRect
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
                painter, option, fontMetric, leftX, topY, brush)

        # draw separation line
        lineStart = QPoint(commentStart.x(),
                commentStart.y() + self.verticalOffset)
        lineEnd = QPoint(lineStart.x() + self.width - 20,
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

        """ Calculate the size of a comment element.

        The size of comment itself (`comment[0]`) is calculated considering
        wordwrapping. The base rectangle, for calculating the bounding rectangle
        of comment is constructed from the height given by `option.rect` and the
        width set by `setWidth`.
        Thus the size of comment wont exceed the width of the widget.
        """

        authorFontMetric = QFontMetrics(self.authorFont)
        commentBoundRect = self.getCommentRect(comment, option)

        commentTextHeight = commentBoundRect.height()
        authorTextHeight = authorFontMetric.height()

        commentWidth = commentBoundRect.width()
        authorDateWidth = authorFontMetric.width(comment[1] + comment[2]) + 10
        # +1 is the separation line that is drawn
        # commentTextHeight / 2 is the offset from the comment text towards the
        # separation line
        height = (commentTextHeight + authorTextHeight +
                self.verticalOffset + self.commentYOffset + 1)
        width = commentWidth if commentWidth > authorDateWidth else authorDateWidth

        size = QSize(width, height)
        return size


    def sizeHint(self, option, index):

        """ Return the size of a comment element. """

        comment = index.model().data(index, Qt.DisplayRole)
        size = self.calcCommentSize(comment, option)

        if index.row() == 0:
            util.debug("Size of the comment: {}".format(size))

        return size


    def getCommentRect(self, comment, option):

        """ Returns the rectangle where just the comment fits in.

        The comment hereby is wordwrapped and won't exceed the widgets width.
        """

        commentFontMetric = QFontMetrics(self.commentFont)

        # calculate the bounding rectangle for comment that fits into the
        # width of the widget.
        rect = self.getWidgetWithRect(option)
        boundRect = commentFontMetric.boundingRect(rect,
                Qt.TextWordWrap | Qt.AlignLeft,
                comment[0])

        return boundRect


    def getWidgetWithRect(self, option):

        """ Returns a rectangle based on `option.rect` where width is replaced
        by `self.width` """

        rect = option.rect
        rect.setWidth(self.width)

        return rect


    @Slot()
    def setWidth(self, newWidth):

        self.width = newWidth
