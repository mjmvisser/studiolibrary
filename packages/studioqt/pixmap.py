#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary/packages/studioqt\pixmap.py
from PySide import QtGui

class Pixmap(QtGui.QPixmap):

    def setColor(self, color):
        """
        :type color: QtGui.QColor
        :rtype: None
        """
        alpha = QtGui.QPixmap(self)
        self.fill(color)
        self.setAlphaChannel(alpha.alphaChannel())
