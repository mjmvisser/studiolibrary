#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary/packages/studioqt\resource.py
import os
from studioqt import QtGui
from studioqt import QtWidgets
import studioqt

class Resource(object):
    DEFAULT_DIRNAME = ''

    def __init__(self, dirname = None):
        """
        :type dirname: str
        """
        dirname = dirname.replace('\\', '/')
        self._dirname = dirname or self.DEFAULT_DIRNAME

    def dirname(self):
        """
        :rtype: str
        """
        return self._dirname

    def get(self, *token):
        """
        :rtype: str
        """
        return os.path.join(self.dirname(), *token)

    def icon(self, name, extension = 'png', color = None):
        """
        :type name: str
        :type extension: str
        :rtype: QtGui.QIcon
        """
        pixmap = self.pixmap(name, extension=extension, color=color)
        return QtGui.QIcon(pixmap)

    def pixmap(self, name, scope = 'icons', extension = 'png', color = None):
        """
        :type name: str
        :type extension: str
        :rtype: QtWidgets.QPixmap
        """
        path = self.get(scope, name + '.' + extension)
        pixmap = studioqt.Pixmap(path)
        if color:
            pixmap.setColor(color)
        return pixmap
