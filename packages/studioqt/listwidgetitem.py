#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/studioqt\listwidgetitem.py
import logging
from PySide import QtGui
from PySide import QtCore
__all__ = ['ListWidgetItem']
logger = logging.getLogger(__name__)

class ListWidgetItem(QtGui.QListWidgetItem):

    def __init__(self, *args, **kwargs):
        QtGui.QListWidgetItem.__init__(self, *args, **kwargs)
        self._url = ''
        self._pixmap = None
        self._iconPath = ''
        self._infoWidget = None

    def dpi(self):
        return self.listWidget().dpi()

    def path(self):
        return ''

    def rect(self):
        return self._rect

    def setRect(self, rect):
        self._rect = rect

    def index(self):
        return self.listWidget().indexFromItem(self)

    def repaint(self):
        index = self.index()
        self.listWidget().update(index)

    def searchText(self):
        return self.text()

    def padding(self):
        return self.listWidget().padding()

    def url(self):
        return QtCore.QUrl(self.text())

    def setUrl(self, url):
        self._url = url

    def iconPath(self):
        return self._iconPath

    def setIconPath(self, path):
        self._iconPath = path

    def sizeHint(self, *args, **kwargs):
        return self.listWidget().viewSize()

    def infoWidget(self):
        pass

    def hideInfoWidget(self):
        if self._infoWidget:
            self._infoWidget.hide()
        self._infoWidget = None

    def showInfoWidget(self):
        self._infoWidget = self.infoWidget(parent=None)
        if self._infoWidget:
            flags = QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
            self._infoWidget.setWindowFlags(flags)
            self._infoWidget.show()
            self.updateInfoWidget()

    def updateInfoWidget(self):
        if self._infoWidget:
            pos = QtGui.QCursor().pos()
            self._infoWidget.move(pos.x() + 20, pos.y() + 20)

    def clicked(self):
        pass

    def doubleClicked(self):
        pass

    def itemSelectionChanged(self, selectedItems, deselectedItems):
        pass

    def mousePressEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideInfoWidget()

    def mouseReleaseEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideInfoWidget()

    def mouseMoveEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.updateInfoWidget()

    def mouseEnterEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideInfoWidget()

    def mouseLeaveEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideInfoWidget()

    def keyPressEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideInfoWidget()

    def keyReleaseEvent(self, event):
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        self.hideInfoWidget()

    def setPixmap(self, pixmap):
        self._pixmap = pixmap

    def pixmap(self):
        if self._pixmap is None and self.iconPath():
            self._pixmap = QtGui.QPixmap(self.iconPath())
        return self._pixmap

    def itemTextHeight(self):
        return self.listWidget().itemTextHeight()

    def isItemTextVisible(self):
        return self.listWidget().isItemTextVisible()

    def textColor(self):
        """
        :rtype: QtGui.QtColor
        """
        return self.listWidget().textColor()

    def textSelectedColor(self):
        """
        :rtype: QtGui.QtColor
        """
        return self.listWidget().textSelectedColor()

    def backgroundColor(self):
        """
        :rtype: QtGui.QtColor
        """
        return self.listWidget().backgroundColor()

    def backgroundHoverColor(self):
        """
        :rtype: QtGui.QtColor
        """
        return self.listWidget().backgroundHoverColor()

    def backgroundSelectedColor(self):
        """
        :rtype: QtGui.QtColor
        """
        return self.listWidget().backgroundSelectedColor()

    def visualRect(self, option):
        """
        :type option:
        :rtype: QtGui.QRect
        """
        visualRect = QtCore.QRect(option.rect)
        if self.listWidget().isListView():
            height = visualRect.height() + self.listWidget().spacing()
            visualRect.setHeight(height)
        return visualRect

    def paint(self, painter, option, index):
        """
        :type painter: QtGui.QPainter
        :type option:
        """
        self.setRect(QtCore.QRect(option.rect))
        painter.save()
        try:
            self.paintBackground(painter, option)
            if self.isItemTextVisible():
                self.paintText(painter, option)
            self.paintIcon(painter, option)
        finally:
            painter.restore()

    def paintBackground(self, painter, option):
        """
        :type painter: QtGui.QPainter
        :type option:
        """
        isSelected = option.state & QtGui.QStyle.State_Selected
        isMouseOver = option.state & QtGui.QStyle.State_MouseOver
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        visualRect = self.visualRect(option)
        if isSelected:
            color = self.backgroundSelectedColor()
            painter.setBrush(QtGui.QBrush(color))
        elif isMouseOver:
            color = self.backgroundHoverColor()
            painter.setBrush(QtGui.QBrush(color))
        else:
            color = self.backgroundColor()
            painter.setBrush(QtGui.QBrush(color))
        painter.drawRect(visualRect)

    def iconRect(self, option):
        padding = self.padding()
        rect = self.visualRect(option)
        width = rect.width()
        height = rect.height()
        if self.listWidget().isIconView():
            height -= self.itemTextHeight()
        else:
            width = height
        width -= padding
        height -= padding
        rect.setWidth(width)
        rect.setHeight(height)
        x = 0
        x += float(padding) / 2
        if self.listWidget().isIconView():
            x += float(width - rect.width()) / 2
        y = float(height - rect.height()) / 2
        y += float(padding) / 2
        rect.translate(x, y)
        return rect

    def paintIcon(self, painter, option, align = None):
        """
        :type painter: QtGui.QPainter
        :type option:
        """
        pixmap = self.pixmap()
        if pixmap and isinstance(pixmap, QtGui.QPixmap):
            iconRect = self.iconRect(option)
            pixmap = pixmap.scaled(iconRect.width(), iconRect.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            pixmapRect = QtCore.QRect(iconRect)
            pixmapRect.setWidth(pixmap.width())
            pixmapRect.setHeight(pixmap.height())
            align = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
            x, y = (0, 0)
            isAlignHCenter = align == QtCore.Qt.AlignHCenter or align == QtCore.Qt.AlignCenter or align == QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom or align == QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop
            isAlignVCenter = align == QtCore.Qt.AlignVCenter or align == QtCore.Qt.AlignCenter or align == QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft or align == QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight
            isAlignBottom = align == QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft or align == QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter or align == QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight
            if isAlignHCenter:
                x += float(iconRect.width() - pixmap.width()) / 2
            if isAlignVCenter:
                y += float(iconRect.height() - pixmap.height()) / 2
            elif isAlignBottom:
                y += float(iconRect.height() - pixmap.height())
            pixmapRect.translate(x, y)
            painter.drawPixmap(pixmapRect, pixmap)

    def paintText(self, painter, option):
        """
        :type painter: QtGui.QPainter
        :type option:
        """
        text = self.text()
        color = self.textColor()
        padding = self.padding()
        visualRect = self.visualRect(option)
        width = visualRect.width() - padding
        height = visualRect.height() - padding
        x = padding / 2
        y = padding / 2
        if self.listWidget().isListView():
            x += self.sizeHint().height() + padding
        visualRect.translate(x, y)
        visualRect.setWidth(width)
        visualRect.setHeight(height)
        font = QtGui.QFont()
        pen = QtGui.QPen(color)
        metrics = QtGui.QFontMetrics(font)
        align = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        if self.listWidget().isIconView():
            if metrics.width(text) > visualRect.width() - self.padding() * 2:
                align = QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom
            else:
                align = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawText(visualRect, align, text)
