#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\core\tempdir.py
import os
import shutil
import getpass
import tempfile
__all__ = ['TempDir']

class TempDir(object):

    def __init__(self, *args, **kwargs):
        """
        :type subDirs: list[str]
        """
        user = getpass.getuser().lower()
        tempdir = tempfile.gettempdir().replace('\\', '/')
        self._path = os.path.join(tempdir, 'studiolibrary', user, *args)
        if kwargs.get('clean', False):
            self.clean()
        if kwargs.get('makedirs', True):
            self.makedirs()

    def path(self):
        """
        :rtype: str
        """
        return self._path

    def clean(self):
        """
        :rtype: str
        """
        if os.path.exists(self.path()):
            shutil.rmtree(self.path())

    def makedirs(self):
        """
        :rtype: str
        """
        if not os.path.exists(self.path()):
            os.makedirs(self.path())
