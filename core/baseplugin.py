#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary\core\baseplugin.py
import os
import inspect
import logging
from studioqt import QtCore
__all__ = ['BasePlugin']
logger = logging.getLogger(__name__)

class BasePlugin(QtCore.QObject):

    def __init__(self, parent = None):
        """
        :type parent: QtWidgets.QWidget
        """
        QtCore.QObject.__init__(self, parent)
        self._name = ''
        self._path = ''
        self._loaded = False

    def dirname(self):
        """
        :rtype: str
        """
        path = inspect.getfile(self.__class__)
        return os.path.dirname(path)

    def setName(self, name):
        """
        :type name: str
        :rtype: None
        """
        self._name = name

    def name(self):
        """
        :rtype: str
        """
        return self._name

    def setPath(self, path):
        """
        :type path: str
        """
        self._path = path

    def path(self):
        """
        :rtype: str
        """
        return self._path

    def isLoaded(self):
        """
        :rtype: bool
        """
        return self._loaded

    def setLoaded(self, value):
        """
        :type value: bool
        """
        self._loaded = value

    def load(self):
        """
        :rtype: None
        """
        pass

    def unload(self):
        """
        :rtype: None
        """
        pass
