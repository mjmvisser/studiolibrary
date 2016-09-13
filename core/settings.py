#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.23.2/build27/studiolibrary\core\settings.py
import os
from . import metafile
__all__ = ['Settings']

class Settings(metafile.MetaFile):
    _instances = {}
    DEFAULT_PATH = os.getenv('APPDATA') or os.getenv('HOME')

    @classmethod
    def instance(cls, scope, name):
        """
        :type scope: str
        :type name: str
        :rtype: Settings
        """
        key = scope + '/' + name
        if key not in cls._instances:
            cls._instances[key] = cls(scope, name)
        return cls._instances[key]

    def __init__(self, scope, name):
        """
        :type scope: str
        :type name: str
        """
        self._path = None
        self._name = name
        self._scope = scope
        metafile.MetaFile.__init__(self, '')

    def path(self):
        """
        :rtype: str
        """
        if not self._path:
            self._path = os.path.join(Settings.DEFAULT_PATH, self._scope, self._name + '.dict')
        return self._path
