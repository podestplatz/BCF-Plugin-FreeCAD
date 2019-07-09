from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import QModelIndex, Slot, QSize, QRect, QPoint, QRectF


class CommentDelegate(QAbstractItemDelegate):

    def __init__(self, parent = None):

        QAbstractItemDelegate.__init__(self, parent)
        self.commentFont = QFont("times", 12)
        self.authorFont = self.commentFont
        self.authorFont.setPixelSize(self.authorFont.pixelSize() - 2)


    def paint(self, painter, option, index):

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())


        painter.save()

        boundingRect = painter.viewport()
        pen = painter.pen()
        self.commentFont = painter.font()
        fontMetric = painter.fontMetrics()
        painter.setBrush(option.palette.text())

        # draw comment
        comment = index.model().data(index, Qt.DisplayRole)
        commentTextHeight = fontMetric.height()
        commentTextWidth = fontMetric.width(comment[0])
        commentStart = QPoint(10, fontMetric.height())

        painter.drawText(commentStart, comment[0])

        # draw separation line
        pen.setColor(QColor("lightGray"))
        painter.setPen(pen)
        lineStart = QPoint(commentStart.x(),
                commentStart.y() + commentTextHeight / 2)
        lineEnd = QPoint(lineStart.x() + boundingRect.width() - 20,
                lineStart.y())
        painter.drawLine(lineStart, lineEnd)

        #TODO: draw author and date
        pen.setColor(QColor("blue"))
        painter.setPen(pen)
        #authorStart = QPoint(lineStart.x(), lineStart.y() +

        print("Drew text: {}".format(comment[0]))

        painter.restore()


    def calcCommentSize(self, comment):

        fontMetric = QFontMetrics(self.commentFont)

        textWidth = fontMetric.width(comment[0])
        textHeight = fontMetric.height()

        size = QSize(textWidth, textHeight)
        print("Size reported: {}".format(size))
        return size


    def sizeHint(self, option, index):

        comment = index.model().data(index, Qt.DisplayRole)
        size = self.calcCommentSize(comment)

        return size
