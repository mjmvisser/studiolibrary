#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/studioqt\pixmap.py
from studioqt import QtGui
from studioqt import QtWidgets
import studioqt

class Pixmap(QtGui.QPixmap):

    def __init__(self, *args):
        QtGui.QPixmap.__init__(self, *args)
        self._color = None

    def setColor(self, color):
        """
        :type color: QtGui.QColor
        :rtype: None
        """
        if isinstance(color, basestring):
            color = studioqt.Color.fromString(color)
        if not self.isNull():
            painter = QtGui.QPainter(self)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
            painter.setBrush(color)
            painter.setPen(color)
            painter.drawRect(self.rect())
            painter.end()
